"""
Orange Labs
Authors : Colin Troisemaine & Vincent Lemaire
Maintainer : colin.troisemaine@gmail.com
"""

from matplotlib import pyplot as plt
from scipy import stats
import pandas as pd
import numpy as np
import Orange
import os


if __name__ == "__main__":
    n_bins = 32

    # The paths to the RMSE table where the results are stored. At least two tables must be given to be compared
    rmse_tables = [
        (os.path.join('..', 'data', 'results_tables', 'equal_freq_below_threshold_RandomForest_classifier_DecisionTree_regressor', 'RMSE_table.csv'), str(n_bins) + ' T Test RMSE', 'DT+'),
        (os.path.join('..', 'data', 'results_tables', 'equal_freq_below_threshold_RandomForest_classifier_DecisionTree_regressor', 'RMSE_table.csv'), 'Base Test RMSE', 'DT'),
        (os.path.join('..', 'data', 'results_tables', 'equal_freq_below_threshold_RandomForest_classifier_LinearRegression_regressor', 'RMSE_table.csv'), str(n_bins) + ' T Test RMSE', 'LR+'),
        (os.path.join('..', 'data', 'results_tables', 'equal_freq_below_threshold_RandomForest_classifier_LinearRegression_regressor', 'RMSE_table.csv'), 'Base Test RMSE', 'LR'),
        (os.path.join('..', 'data', 'results_tables', 'equal_freq_below_threshold_RandomForest_classifier_RandomForest_regressor', 'RMSE_table.csv'), str(n_bins) + ' T Test RMSE', 'RF+'),
        (os.path.join('..', 'data', 'results_tables', 'equal_freq_below_threshold_RandomForest_classifier_RandomForest_regressor', 'RMSE_table.csv'), 'Base Test RMSE', 'RF'),
        (os.path.join('..', 'data', 'results_tables', 'equal_freq_below_threshold_Khiops_classifier_Khiops_regressor', 'RMSE_table.csv'), 'Base Test RMSE', 'Khiops'),
        (os.path.join('..', 'data', 'results_tables', 'equal_freq_below_threshold_Khiops_classifier_Khiops_regressor', 'RMSE_table.csv'), str(n_bins) + ' T Test RMSE', 'Khiops+')
    ]

    # The method that is compared with other methods If omitted, show pairwise comparison of methods
    cdmethod = None

    groups = []
    # Get for each table the column corresponding to the parameters
    for path, column, _ in rmse_tables:
        tmp_df = pd.read_csv(path)
        groups.append(list(tmp_df[column]))

    # Rank the data for each dataset
    ranked_data = [list(stats.rankdata(row)) for row in np.array(groups).T]

    average_ranks = [np.mean(vect) for vect in np.array(ranked_data).T]

    cd = Orange.evaluation.compute_CD(average_ranks, len(groups[0]))
    Orange.evaluation.graph_ranks(average_ranks, [vect[2] for vect in rmse_tables], cd=cd, width=6, textspace=1.5, cdmethod=cdmethod)
    plt.savefig('critical_diagram_' + str(n_bins) + 'bins.png')
