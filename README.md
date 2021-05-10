# Classification For Regression

## Directory Structure
    .
    ├── .gitignore
    ├── README.md                                   <- This file
    ├── requirements.txt                            <- The required packages
    ├── data                                        <- The datasets in their different forms
    │   ├── extracted_features                      <- The datasets augmented with the extracted features
    │   ├── logs                                    <- The logs generated by the scripts
    │   ├── processed                               <- The datasets after pre-processing and discretization
    │   └── raw                                     <- The original datasets
    │   │   └── Combined_Cycle_Power_Plant_Dataset  <- A sample dataset
    ├── notebooks                                   <- The jupyter notebooks
    │   └── Datasets_First_Study.ipynb              <- Notebook to check the datasets
    ├── scripts                                     <- The scripts
    │   ├── compute_test_metrics.py                 <- Used to compute regression performance on a dataset folder
    │   ├── data_processing.py                      <- Used to pre-process a dataset
    │   └── feature_extraction.py                   <- Used to extract the features of a dataset folder
    └── src                                         <- The source code
        ├── class_generation                        <- The discretization methods
        │   ├── BelowThresholdClassGenerator.py     <- Data under the thresholds are given a 1, others a 0
        │   ├── CustomClassGenerator.py             <- The abstract class to inherit from
        │   └── InsideBinClassGenerator.py          <- Thresholds define bins with classes numbers
        ├── models                                  <- The models used for classification or regression
        │   ├── BaseModel.py                        <- The abstract classification model to inherit from
        │   └── RandomForestC.py                    <- The random forests classifier
        ├── steps_encoding                          <- The thresholds generation methods
        │   ├── EqualFreqStepsEncoder.py            <- Generates thresholds with equal frequency
        │   ├── EqualWidthStepsEncoder.py           <- Generates thresholds with equal width
        │   └── StepsEncoder.py                     <- The abstract class to inherit from
        └── utils                                   <- Various utility methods
            ├── DataProcessingUtils.py              <- Methods used to pre-prorcess the datasets
            └── logging_util.py                     <- Message logging utility methods


## Install
This project requires python 3.7 and the librairies described in requirements.txt.

It is recommended to create a virtual environment with virtualenv to install the exact versions of the packages used in this project. You will first need to install *virtualenv* with pip :
> pip install virtualenv

Then create the virtual environment :
> virtualenv my_python_environment

And finally activate it using :
> source my_python_environment/bin/activate

At this point, you should see the name of your virtual environment in parentheses on your terminal line.

You can now install the required libraries inside your virtual environment with :
> pip install -r requirements.txt


## Run
Here is a list of examples of usages of the scripts :

Pre-processing of a dataset :
> python data_processing.py --dataset_path="../data/raw/Combined_Cycle_Power_Plant_Dataset/Folds5x2_pp.csv" --output_path="../data/processed/Combined_Cycle_Power_Plant_Dataset" --goal_var_index=4

Extracting the features of a pre-processed dataset using classification :
> python feature_extraction.py --dataset_folder="../data/processed/Combined_Cycle_Power_Plant_Dataset/" --output_path="../data/extracted_features/Combined_Cycle_Power_Plant_Dataset/" --classifier="RandomForests"

Compute metrics using a regression model :
> python compute_test_metrics.py --dataset_folder="../data/processed/Combined_Cycle_Power_Plant_Dataset/" --regressor="RandomForests"


## Usage
Here are the scripts and the details about every usable parameter :

1) **data_processing.py :**
    > python data_processing.py [dataset_path] [output_path] [options]
   
    The mandatory parameters are :
    * dataset_path : The dataset to process
    * output_path : The folder where the results will be saved
   
    The options are :
    * split_method : The splitting method to use
    * output_classes : The method of class generation
    * delimiter : Delimiter to use when reading the dataset
    * header : Infer the column names or use None if the first line isn't a csv header line
    * decimal : Character to recognize as decimal point
    * na_values : Additional string to recognize as NA/NaN
    * usecols : The indexes of the columns to keep
    * goal_var_index : The index of the column to use as the goal variable
    * n_bins : The number of bins to create
    * k_folds : The number of folds in the k-folds
    * log_lvl : Change the log display level

2) **feature_extraction.py :**
    > python feature_extraction.py [dataset_folder] [output_path] [options]

    The mandatory parameters are :
    * dataset_folder : The folder where the k-fold datasets are stored
    * output_path : The folder where the results will be saved

    The options are :
    * classifier : The classifier model to use
    * class_cols : The indexes of the classes columns
    * log_lvl : Change the log display level
   

3) **compute_test_metrics.py :**
    > python compute_test_metrics.py [dataset_folder] [regressor] [options]

    The mandatory parameters are :
    * dataset_folder : The folder where the test and train k-fold datasets are stored
    * regressor : The regression model to use

    The options are :
    * log_lvl : Change the log display level