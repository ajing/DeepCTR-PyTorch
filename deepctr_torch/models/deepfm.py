# -*- coding:utf-8 -*-
"""
Author:
    Weichen Shen,wcshen1994@163.com
Reference:
    [1] Guo H, Tang R, Ye Y, et al. Deepfm: a factorization-machine based neural network for ctr prediction[J]. arXiv preprint arXiv:1703.04247, 2017.(https://arxiv.org/abs/1703.04247)
"""
import torch
import torch.nn as nn
import torch.nn.functional as F

from .basemodel import BaseModel
from ..inputs import combined_dnn_input
from ..layers import FM, DNN


class DeepFM(BaseModel):

    def __init__(self,
                 linear_feature_columns, dnn_feature_columns, embedding_size=8, use_fm=True,
                 dnn_hidden_units=(256, 128),
                 l2_reg_linear=0.00001, l2_reg_embedding=0.00001, l2_reg_dnn=0, init_std=0.0001, seed=1024,
                 dnn_dropout=0,
                 dnn_activation=F.relu, dnn_use_bn=False, task='binary', device='cpu'):
        """Instantiates the DeepFM Network architecture.
        :param linear_feature_columns: An iterable containing all the features used by linear part of the model.
        :param dnn_feature_columns: An iterable containing all the features used by deep part of the model.
        :param embedding_size: positive integer,sparse feature embedding_size
        :param use_fm: bool,use FM part or not
        :param dnn_hidden_units: list,list of positive integer or empty list, the layer number and units in each layer of DNN
        :param l2_reg_linear: float. L2 regularizer strength applied to linear part
        :param l2_reg_embedding: float. L2 regularizer strength applied to embedding vector
        :param l2_reg_dnn: float. L2 regularizer strength applied to DNN
        :param init_std: float,to use as the initialize std of embedding vector
        :param seed: integer ,to use as random seed.
        :param dnn_dropout: float in [0,1), the probability we will drop out a given DNN coordinate.
        :param dnn_activation: Activation function to use in DNN
        :param dnn_use_bn: bool. Whether use BatchNormalization before activation or not in DNN
        :param task: str, ``"binary"`` for  binary logloss or  ``"regression"`` for regression loss
        :param device:
        :return: A PyTorch model instance.
        """

        super(DeepFM, self).__init__(linear_feature_columns, dnn_feature_columns, embedding_size=embedding_size,
                                     dnn_hidden_units=dnn_hidden_units,
                                     l2_reg_linear=l2_reg_linear,
                                     l2_reg_embedding=l2_reg_embedding, l2_reg_dnn=l2_reg_dnn, init_std=init_std,
                                     seed=seed,
                                     dnn_dropout=dnn_dropout, dnn_activation=dnn_activation,
                                     task=task, device=device)

        self.use_fm = use_fm
        self.use_dnn = len(dnn_feature_columns) > 0 and len(
            dnn_hidden_units) > 0
        if use_fm:
            self.fm = FM()

        if self.use_dnn:
            self.dnn = DNN(self.compute_input_dim(dnn_feature_columns, embedding_size, ), dnn_hidden_units,
                           activation=dnn_activation, l2_reg=l2_reg_dnn, dropout_rate=dnn_dropout, use_bn=dnn_use_bn, init_std=init_std, device=device)
            self.dnn_linear = nn.Linear(
                dnn_hidden_units[-1], 1, bias=False).to(device)

            self.add_regularization_loss(
                filter(lambda x: 'weight' in x[0] and 'bn' not in x[0], self.dnn.named_parameters()), l2_reg_dnn)
            self.add_regularization_loss(self.dnn_linear.weight, l2_reg_dnn)
        self.to(device)

    def forward(self, X):

        sparse_embedding_list, dense_value_list = self.input_from_feature_columns(X, self.dnn_feature_columns,
                                                                                  self.embedding_dict)
        logit = self.linear_model(X)

        if self.use_fm and len(sparse_embedding_list) > 0:
            fm_input = torch.cat(sparse_embedding_list, dim=1)
            logit += self.fm(fm_input)

        if self.use_dnn:

            dnn_input = combined_dnn_input(
                sparse_embedding_list, dense_value_list)
            dnn_output = self.dnn(dnn_input)
            dnn_logit = self.dnn_linear(dnn_output)
            logit += dnn_logit

        y_pred = self.out(logit)

        return y_pred