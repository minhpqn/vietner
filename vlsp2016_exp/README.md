# Experiments on VLSP 2016 NER data

In order to run experiments on VLSP 2016 data, you just need to run
the shell script `run.sh`

You may need to change the paths to training, test data, output directories
in the shell scripts and configuration files in the directory [./config](./config)


## VLSP 2016 NER data

Since we do not address nested entities in paper [1](https://arxiv.org/abs/1803.04375), each line in
training and test data file should have 4 fields `w pos chunk tag`, separated
by a tab or a space character. If fields are separated by a tab, you should
run the script `run.sh` with the argument `run.sh -tab`.

You need to change the path to training/test data in the shell script `run.sh`.

## How to run

Use the script `main.py` as follows.

When we run on the sample data where space character is used as the separator.

```
python main.py ./config/config1.yml tmp/ ./data/train_sample-space.txt ./data/test_sample-space.txt
```

IWhen we run on the sample data where tab character is used as the separator.

```
python main.py -tab ./config/config1.yml tmp/ ./data/train_sample-tab.txt ./data/test_sample-tab.txt
```

