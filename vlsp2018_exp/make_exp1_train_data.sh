#!/usr/bin/env bash

trainDir="./data/VLSP2018-NER-train-Jan14"
dataDir="./data/exp1/train"

mkdir -p $dataDir

python word_segment.py $trainDir $dataDir/train_syllables.txt $dataDir/train_ws.txt &> $dataDir/log-train.txt

cut -f 1,2 -d " " $dataDir/train_ws.txt > $dataDir/train_ws-l1.txt
cut -f 1,3 -d " " $dataDir/train_ws.txt > $dataDir/train_ws-l2.txt
cut -f 1,4 -d " " $dataDir/train_ws.txt > $dataDir/train_ws-l3.txt
python join_tags2.py -o $dataDir/train_ws-l1+l2.txt $dataDir/train_ws-l1.txt $dataDir/train_ws-l2.txt



