#!/bin/sh

devOutputDir="./data/exp1/output/dev"
testOutputDir="./data/exp1/output/test"

mkdir -p $devOutputDir
mkdir -p testOutputDir

# Preprocess dev data and test data

# python preprocess_test_data.py $devData $devOutputDir/VLSP_NER_dev_ws.csv

# python preprocess_test_data.py $testData $testOutputDir/VLSP_NER_test_ws.csv

# Generate output of experiment 1 for the development set

# python gen_ner_result.py -l1_model ./data/exp1/models/l1_model/model.bin -l2_model ./data/exp1/models/l2_model/model.bin -joint_model ./data/exp1/models/joint_model/model.bin ./data/exp1/output/dev/VLSP_NER_dev_ws.csv ./data/VLSP2018-NER-dev ./data/exp1/output/dev/

# Generate output of experiment 1 for the test set

python gen_ner_result.py -l1_model ./data/exp1/models/l1_model/model.bin -l2_model ./data/exp1/models/l2_model/model.bin -joint_model ./data/exp1/models/joint_model/model.bin ./data/exp1/output/test/VLSP_NER_test_ws.csv ./data/VLSP2018-NER-Test-Domains ./data/exp1/output/test/









