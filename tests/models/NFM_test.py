# -*- coding: utf-8 -*-
import pytest
import sys
from deepctr_torch.models import NFM
from ..utils import check_model, get_test_data, SAMPLE_SIZE


@pytest.mark.parametrize(
    'hidden_size,sparse_feature_num',
    [((8,), 2), ((8, 8,), 2), ((8,), 1)]
)
def test_NFM(hidden_size, sparse_feature_num):

    model_name = "NFM"

    sample_size = SAMPLE_SIZE
    x, y, feature_columns = get_test_data(
        sample_size, sparse_feature_num, sparse_feature_num)

    model = NFM(feature_columns, feature_columns, embedding_size=8,
                dnn_hidden_units=[32, 32], dnn_dropout=0.5)
    check_model(model, model_name, x, y)


if __name__ == "__main__":
    pass