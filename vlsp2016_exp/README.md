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

When we run on the sample data where tab character is used as the separator.

```
python main.py -tab ./config/config1.yml tmp/ ./data/train_sample-tab.txt ./data/test_sample-tab.txt
```

## Experimental Results on VLSP 2016 data set

Following table shows the experimental results with three settings:

- Using *Original POS and chunking tags* provided in the data. In this setting,
we use all features derived from words, POS tags, chunking tags
- *Without chunking tags*: we use features derived from words and POS tags
- *Without POS, chunking tags*: we use only features derived from words

We use Precision, Recall, F1 as evaluation measures. These measures are calculated
using the perl script `conlleval`.

**Note**: we modified some annotation mistakes in the training and test data
(e.g., missing B- tags), so the following results may be different from
the reported results in the paper [\[1\]](https://arxiv.org/abs/1803.04375).

| Setting                      | Precision | Recall | F1   |
|--------------------------------|-----------|--------|------|
|Original POS and chunking tags  | 93.68     | 94.03  | 93.85 |
|Without chunking tags | 90.13 | 90.49 | 90.31 |
|Without POS, chunking tags | 89.93 | 90.29 | 90.11 |

## Citation

Please cite the following paper when you compare your NER model with
**vietner** on the VLSP 2016 data set in your paper.

```
@article{minh2018a,
  title={A Feature-Rich Vietnamese Named-Entity Recognition Model},
  author={Minh, Pham Quang Nhat},
  journal={Proceedings of CICLING 2018},
  year={2018}
}
```

