# -*- coding: utf-8 -*-
import pytest
import sys
from deepctr_torch.models import DCN
from ..utils import check_model, get_test_data, SAMPLE_SIZE


@pytest.mark.parametrize(
    'embedding_size,cross_num,hidden_size,sparse_feature_num',
    [(8, 0, (32,), 2),
     ]  # ('auto', 1, (32,), 3) , ('auto', 1, (), 1), ('auto', 1, (32,), 3)
)
def test_DCN(embedding_size, cross_num, hidden_size, sparse_feature_num):
    model_name = "DCN"

    sample_size = SAMPLE_SIZE
    x, y, feature_columns = get_test_data(
        sample_size, sparse_feature_num, sparse_feature_num)

    model = DCN(feature_columns, embedding_size=embedding_size,
                cross_num=cross_num, dnn_hidden_units=hidden_size, dnn_dropout=0.5)
    check_model(model, model_name, x, y)


if __name__ == "__main__":
    pass