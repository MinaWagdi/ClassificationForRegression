"""
Orange Labs
Authors : Colin Troisemaine & Vincent Lemaire
contact : colin.troisemaine@gmail.com
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.class_generation.BelowThresholdClassGenerator import BelowThresholdClassGenerator
from src.class_generation.InsideBinClassGenerator import InsideBinClassGenerator
from src.steps_encoding.EqualWidthStepsEncoder import EqualWidthStepsEncoder
from src.steps_encoding.EqualFreqStepsEncoder import EqualFreqStepsEncoder
from src.utils.logging_util import setup_logging_level
from src.utils.DataProcessingUtils import *
import pandas as pd
import numpy as np
import argparse
import logging
import ntpath
import time
import os


def argument_parser():
    """
    A parser to allow user to easily process any dataset using the split method and class generation he desires.
    """

    parser = argparse.ArgumentParser(usage='\n python data_processing.py [dataset_path] [output_path] [split_method] '
                                           '[output_classes] [delimiter] [header] [decimal] [na_values] [usecols] '
                                           '[goal_var_index] [n_bins] [k_folds] [log_lvl]',
                                     description="This program allows to process datasets to be used later.")

    parser.add_argument('--dataset_path',
                        type=str,
                        help='The dataset to process',
                        required=True)

    parser.add_argument('--output_path',
                        type=str,
                        help='The folder where the results will be saved',
                        required=True)

    parser.add_argument('--split_method',
                        type=str,
                        default="equal_freq",
                        choices=["equal_width", "equal_freq", "kmeans"],
                        help='The splitting method to use')

    parser.add_argument('--output_classes',
                        type=str,
                        default="below_threshold",
                        choices=["below_threshold", "inside_bin"],
                        help='The method of class generation')

    parser.add_argument('--delimiter',
                        type=str,
                        default=',',
                        help='Delimiter to use when reading the dataset')

    parser.add_argument('--header',
                        type=str,
                        default="infer",
                        choices=["infer", "None"],
                        help='Infer the column names or use None if the first line isn\'t a csv header line')

    parser.add_argument('--decimal',
                        type=str,
                        default='.',
                        help='Character to recognize as decimal point')

    parser.add_argument('--na_values',
                        type=str,
                        help='Additional string to recognize as NA/NaN')

    parser.add_argument('--usecols',
                        type=int,
                        nargs='*',  # 0 or more values expected
                        help='The indexes of the columns to keep')

    parser.add_argument('--goal_var_index',
                        type=int,
                        required=True,
                        help='The index of the column to use as the goal variable')

    parser.add_argument('--n_bins',
                        type=int,
                        default=10,
                        help='The number of bins to create')

    parser.add_argument('--k_folds',
                        type=int,
                        default=10,
                        help='The number of folds in the k-folds')

    parser.add_argument('--log_lvl',
                        type=str,
                        default='info',
                        choices=["debug", "info", "warning"],
                        help='Change the log display level')

    return parser.parse_args()


if __name__ == "__main__":
    args = argument_parser()

    # Get the current configuration
    dataset_path = args.dataset_path
    output_path = args.output_path
    split_method = args.split_method
    output_classes = args.output_classes
    delimiter = args.delimiter
    header = args.header
    decimal = args.decimal
    na_values = args.na_values
    usecols = args.usecols
    goal_var_index = args.goal_var_index
    n_bins = args.n_bins
    k_folds = args.k_folds

    # Setup the logging level
    setup_logging_level(args.log_lvl)

    # Declare the thresholds generator
    thresholds_generator = None
    if split_method == "equal_width":
        thresholds_generator = EqualWidthStepsEncoder()
    elif split_method == "equal_freq":
        thresholds_generator = EqualFreqStepsEncoder()
    elif split_method == "kmeans":
        # (optional) TODO
        raise ValueError('This split method has not been implemented yet.')
    else:
        raise ValueError('Unknown parameter for split_method.')

    # Declare the class generator
    class_generator = None
    if output_classes == "below_threshold":
        class_generator = BelowThresholdClassGenerator()
    elif output_classes == "inside_bin":
        class_generator = InsideBinClassGenerator()
    else:
        raise ValueError('Unknown parameter for output_classes.')

    logging.info("Reading the dataset's file...")
    reading_start_time = time.time()
    imported_dataset = pd.read_csv(dataset_path, delimiter=delimiter, header=header, decimal=decimal,
                                   na_values=na_values, usecols=usecols)
    logging.info("Dataset imported ({0:.2f}".format(time.time() - reading_start_time) + "sec)")

    # We keep all the columns except the goal variable one
    X = imported_dataset.drop(imported_dataset.columns[goal_var_index], axis=1)
    Y = imported_dataset[imported_dataset.columns[goal_var_index]]

    logging.debug("Dataset's first 3 rows :")
    logging.debug('X :\n' + str(X.head(3)))
    logging.debug('Y :\n' + str(Y.head(3)))

    # TODO : Categorical data encoding => Maybe do that in another script (or even in a notebook)

    k_fold_indexes = kfold_train_test_split(len(Y), k_folds)

    # We iterate for k_folds folds to create the datasets
    for k_fold_index in range(0, k_folds):
        logging.debug("========== FOLD N°" + str(k_fold_index) + " ==========")

        # Get the training and testing indexes based on the k_fold_indexes and the k_fold_index
        train_indexes = []
        test_indexes = []
        for group in range(k_folds):
            if group == k_fold_index:
                test_indexes.append(k_fold_indexes[group])
            else:
                train_indexes.append(k_fold_indexes[group])
        train_indexes = np.concatenate(train_indexes).ravel()  # Ravel the list of lists of indexes
        test_indexes = np.concatenate(test_indexes).ravel()

        X_train, Y_train = X.iloc[train_indexes].copy(), np.array(Y.iloc[train_indexes])
        X_test, Y_test = X.iloc[test_indexes].copy(), np.array(Y.iloc[test_indexes])

        # Fits the box-cox on Y_train and applies it on Y_train AND Y_test
        Y_train, Y_test = box_cox(Y_train, Y_test)

        # Fits the normalization on Y_train and applies it on Y_train AND Y_test
        X_train, X_test = normalize(X_train, X_test)

        # Thresholds definition
        thresholds_list = thresholds_generator.generate_steps(Y_train, n_bins)
        logging.debug("Thresholds :" + str(thresholds_list))

        # Discretization
        class_generator.fit(thresholds_list)
        train_discretized_classes, test_discretized_classes = class_generator.transform(Y_train, Y_test)
        logging.debug("Generated classes (for train dataset) :\n"
                      + str(pd.DataFrame(train_discretized_classes).head(5)))

        # We then add the generated classes to the dataframe
        # If there is only one column of class add it directly
        if type(train_discretized_classes[0]) == int:
            X_train['class'] = train_discretized_classes
            X_test['class'] = test_discretized_classes
        # But if there are multiple class columns, add each of them to the dataframe
        else:
            for class_index in range(len(train_discretized_classes[1])):
                X_train['class_' + str(class_index)] = train_discretized_classes[:, class_index]
                X_test['class_' + str(class_index)] = test_discretized_classes[:, class_index]

        # And finally add the (box-cox transformed) goal variable to be used by the upcoming regression
        X_train['reg_goal_var'] = Y_train
        X_test['reg_goal_var'] = Y_test

        logging.debug("Final dataframe (train) :\n" + str(X_train.head(3)))

        # Save the result in a CSV file
        if not os.path.exists(output_path):
            os.mkdir(output_path)
        train_output_name = os.path.join(output_path,
                                         'fold_' + str(k_fold_index) + '_TRAIN_' + ntpath.basename(dataset_path))
        X_train.to_csv(path_or_buf=train_output_name, index=False)

        test_output_name = os.path.join(output_path,
                                        'fold_' + str(k_fold_index) + '_TEST_' + ntpath.basename(dataset_path))
        X_test.to_csv(path_or_buf=test_output_name, index=False)

        logging.info("Split " + str(k_fold_index) + " datasets saved in files")
