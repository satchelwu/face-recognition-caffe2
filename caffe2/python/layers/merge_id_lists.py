# Copyright (c) 2016-present, Facebook, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##############################################################################

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from caffe2.python import schema
from caffe2.python.layers.layers import (
    get_categorical_limit,
    ModelLayer,
    IdList
)

import numpy as np


class MergeIdLists(ModelLayer):
    """Merge multiple ID_LISTs into a single ID_LIST

    Arguments:
        model: A layer model instance
        input_record: Tuple (Struct) of ID_LIST features to be
        merged

    Returns:
        the merged ID_LIST feature
    """
    def __init__(self, model, input_record, name='merged'):
        super(MergeIdLists, self).__init__(model, name, input_record)
        assert all(schema.equal_schemas(x, IdList) for x in input_record), \
            "Inputs to MergeIdLists should all be IdLists."

        assert all(record.items.metadata is not None
                   for record in self.input_record), \
            "Features without metadata are not supported"

        merge_dim = max(get_categorical_limit(record)
                        for record in self.input_record)
        assert merge_dim is not None, "Unbounded features are not supported"

        self.output_schema = schema.NewRecord(
            model.net, schema.List(
                schema.Scalar(
                    np.int64,
                    blob=model.net.NextBlob(name),
                    metadata=schema.Metadata(categorical_limit=merge_dim)
                )))

    def add_ops(self, net):
        return net.MergeIdLists(self.input_record.field_blobs(),
                                self.output_schema.field_blobs())
