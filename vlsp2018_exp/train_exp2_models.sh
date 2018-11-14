#!/bin/sh

modelDir="./data/exp2/models"
trainDir="./data/exp2/train"

mkdir -p $modelDir

# Training NER Model for level-1 entities

python train.py ./config_files/config1.yml $modelDir/l1_model $trainDir/train_ws-l1.txt

# Training NER Model for level-2 entities

python train.py ./config_files/config1.yml $modelDir/l2_model $trainDir/train_ws-l2.txt

# Training NER Model for joint tags

python train.py ./config_files/config1.yml $modelDir/joint_model $trainDir/train_ws-l1+l2.txt

