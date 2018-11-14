#!/bin/sh

# Please change the path to the VLSP 2016 data
# We omit nested entity so the data file should have 4 columns in each line
# w pos chunk tag

train_data="./data/original/train.4column.txt"
test_data=./data/original/test.4column.txt
opt=""

if [ $# -eq 1 ]
then
   opt="-tab"
fi

# Experiment 1: Using gold-standard POS and chunking tags provided by VLSP 2016 organizers

python main.py $opt ./config/config1.yml output/config1 $train_data $test_data

# Experiment 2: Just using gold-standard POS tags provided by VLSP 2016 organizers

python main.py $opt ./config/config2.yml output/config2 $train_data $test_data

# Experiment 3: Just use features derived from word features

python main.py $opt ./config/config3.yml output/config3 $train_data $test_data