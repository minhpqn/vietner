#!/bin/sh

testOutputDir="./data/exp2/output/test"

mkdir -p $devOutputDir
mkdir -p testOutputDir

# Preprocess dev data and test data

python preprocess_test_data.py $testData $testOutputDir/VLSP_NER_test_ws.csv

# Generate output of experiment 2 for the test set

python gen_ner_result.py -l1_model ./data/exp2/models/l1_model/model.bin -l2_model ./data/exp2/models/l2_model/model.bin -joint_model ./data/exp2/models/joint_model/model.bin ./data/exp2/output/test/VLSP_NER_test_ws.csv ./data/VLSP2018-NER-Test-Domains ./data/exp2/output/test/









