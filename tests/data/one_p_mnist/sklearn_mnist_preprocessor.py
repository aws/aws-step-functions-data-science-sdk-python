# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.
from __future__ import print_function, absolute_import

import argparse
import numpy as np
import os
import gzip

from six import BytesIO

from sklearn.compose import make_column_transformer
from sklearn.externals import joblib
from sklearn.preprocessing import StandardScaler


def create_preprocessing_pipeline(num_columns):
    preprocessor = make_column_transformer(
        (np.arange(num_columns), StandardScaler()),
        remainder='passthrough'
    )
    return preprocessor


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Data and model checkpoints directories
    parser.add_argument("--epochs", type=int, default=-1)
    parser.add_argument("--output-data-dir", type=str, default=os.environ["SM_OUTPUT_DATA_DIR"])
    parser.add_argument("--model-dir", type=str, default=os.environ["SM_MODEL_DIR"])
    parser.add_argument("--train", type=str, default=os.environ["SM_CHANNEL_TRAIN"])
    parser.add_argument("--test", type=str, default=os.environ["SM_CHANNEL_TEST"])
    args = parser.parse_args()

    # Load the data into memory as numpy arrays
    data_path = os.path.join(args.train, "mnist.npy.gz")
    with gzip.open(data_path, "rb") as f:
        data = np.load(f, allow_pickle=True)
    train_set = data[0]
    test_set = data[1]
    train_file = {'x': train_set[:, 1:], 'y': train_set[:, 0]}

    preprocessor = create_preprocessing_pipeline(train_file['x'].shape[1])
    preprocessor.fit(X=train_file['x'], y=train_file['y'])
    joblib.dump(preprocessor, os.path.join(args.model_dir, "model.joblib"))
    print("saved model!")


def input_fn(input_data, content_type):
    # Load the data into memory as numpy arrays
    buf = BytesIO(input_data)
    data = np.load(buf, allow_pickle=True)
    train_set = data[0]
    return train_set[:50, :]


def predict_fn(data, model):
    transformed = np.concatenate((data[:, 0].reshape(-1, 1), model.transform(data[:, 1:])), axis=1)
    return transformed


def model_fn(model_dir):
    clf = joblib.load(os.path.join(model_dir, "model.joblib"))
    return clf
