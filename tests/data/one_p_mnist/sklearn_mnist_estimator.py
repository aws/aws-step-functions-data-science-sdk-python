# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at

#   http://www.apache.org/licenses/LICENSE-2.0

# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.
from __future__ import print_function, absolute_import

import argparse
import numpy as np
import os
import json

from six import BytesIO

from sklearn import svm
from sklearn.externals import joblib


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Data and model checkpoints directories
    parser.add_argument("--epochs", type=int, default=-1)
    parser.add_argument("--output-data-dir", type=str, default=os.environ["SM_OUTPUT_DATA_DIR"])
    parser.add_argument("--model-dir", type=str, default=os.environ["SM_MODEL_DIR"])
    parser.add_argument("--train", type=str, default=os.environ["SM_CHANNEL_TRAIN"])
    args = parser.parse_args()

    # Load the data into memory as numpy arrays
    data_path = os.path.join(args.train, "mnist.npy.gz.out")
    with open(data_path, 'r') as f:
        jsonarray = json.loads(f.read())
        data = np.array(jsonarray)
    train_set = data
    train_file = {'x': train_set[:, 1:], 'y': train_set[:, 0]}

    # Set up a Support Vector Machine classifier to predict digit from images
    clf = svm.SVC(gamma=0.001, C=100.0, max_iter=args.epochs)

    train_images = train_file['x']
    train_labels = train_file['y']
    # Fit the SVM classifier with the images and the corresponding labels
    clf.fit(train_images, train_labels)

    # Print the coefficients of the trained classifier, and save the coefficients
    joblib.dump(clf, os.path.join(args.model_dir, "model.joblib"))


def input_fn(input_data, content_type):
    # Load the data into memory as numpy arrays
    buf = BytesIO(input_data)
    jsonarray = json.loads(buf.read())
    data = np.array(jsonarray)
    return data


def predict_fn(data, model):
    train_set = data[:, 1:]
    return model.predict(train_set)


def model_fn(model_dir):
    clf = joblib.load(os.path.join(model_dir, "model.joblib"))
    return clf
