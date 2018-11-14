#!/usr/bin/env bash

trainDir="./data/VLSP2018-NER-train+dev"
testDir="./data/VLSP2018-NER-Test-Domains"

# combine train/dev dataset into one directory
python join_dir.py $trainDir

# For training data
dataDir="./data/exp2/train"

mkdir -p $dataDir

python word_segment.py $trainDir $dataDir/train_syllables.txt $dataDir/train_ws.txt > $dataDir/log-train.txt

cut -f 1,2 -d " " $dataDir/train_ws.txt > $dataDir/train_ws-l1.txt
cut -f 1,3 -d " " $dataDir/train_ws.txt > $dataDir/train_ws-l2.txt
cut -f 1,4 -d " " $dataDir/train_ws.txt > $dataDir/train_ws-l3.txt
python join_tags2.py -o $dataDir/train_ws-l1+l2.txt $dataDir/train_ws-l1.txt $dataDir/train_ws-l2.txt


# For test set
dataDir="./data/exp2/test"

mkdir -p $dataDir

python word_segment.py $testDir $dataDir/test_syllables.txt $dataDir/test_ws.txt > $dataDir/log-test.txt

cut -f 1,2 -d " " $dataDir/test_ws.txt > $dataDir/test_ws-l1.txt
cut -f 1,3 -d " " $dataDir/test_ws.txt > $dataDir/test_ws-l2.txt
cut -f 1,4 -d " " $dataDir/test_ws.txt > $dataDir/test_ws-l3.txt
python join_tags2.py -o $dataDir/test_ws-l1+l2.txt $dataDir/test_ws-l1.txt $dataDir/test_ws-l2.txt

