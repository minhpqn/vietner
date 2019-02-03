# vietner: A Feature-based Vietnamese Named-Entity Recognition Model

Author: Pham Quang Nhat Minh

**vietner** is a feature-based named-entity recognition
model that obtained very strong results on VLSP 2016
and VLSP 2018 NER data sets. In VLSP 2018 evaluation
campaign, **vietner** obtained the first rank among
participant systems.

Details of the model and features used in the model
can be found in the following papers.

1. Pham Quang Nhat Minh (2018). [A Feature-Rich Vietnamese Named-Entity Recognition Model](https://arxiv.org/abs/1803.04375). arXiv preprint arXiv:1803.04375.
2. Pham, M. Q. N. (2018). A Feature-Based Model for Nested Named-Entity Recognition at VLSP-2018 NER Evaluation Campaign. Journal of Computer Science and Cybernetics, 34(4), 311-321. Link: [http://www.vjs.ac.vn/index.php/jcc/article/view/13163](http://www.vjs.ac.vn/index.php/jcc/article/view/13163)

## Requirements

- Python 3.6.3
- regex
- Perl (version 5)
- yaml
- pandas
- nltk
- [crfsuite 0.12](http://www.chokkan.org/software/crfsuite/)

## Resources

In experiments on VLSP 2016 and VLSP 2018 NER data, we used following resources.

- glove vectors
- word2vec vectors
- Brown word clusters with 1000 clusters.
- Brown word clusters with 5120 clusters

Details of above resources can be found in the paper \[1\].

You can download above resources on this [link](https://drive.google.com/file/d/1q2mBfnHS29-Kkl1cOS68aJeLq-zD6v4X/view?usp=sharing). After downloading the
resource file `resources.zip`, uncompress the file into the root directory of
`vietner` directory.

## Experimental results on VLSP 2016 data set

Go to the directory [./vlsp2016_exp](./vlsp2016_exp) and perform the shell script `run.sh`.

For the details see the [README.md](./vlsp2016_exp/README.md) file the the directory vlsp2016_exp.

You may need to change the paths to training, test data, output directories
in the shell scripts and configuration files in the directory [./vlsp2016_exp/config](./vlsp2016_exp/config)

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


## Experimental results on VLSP 2018 data set

See the [README.md](./vlsp2018_exp/README.md) within the directory [vlsp2018_exp](./vlsp2018_exp)
for more details.

We report experimental results of three systems as follows. The evaluation measures
were calculated by using the official evaluation program [`evaluation.jar`](./vlsp2018_exp/evaluation.jar) that was
provided by VLSP 2018 organizers. The program calculated Precision, Recall, F1 scores
for all named entities including nested entities. We only reported overall evaluation without taking *Domains* into account.

- **Joint**: We use joint model to recognize joint tags for each token of
a sequence, then split joint tags into level-1 and level-2 tags. This is the method used in
the run 4 described in the paper [\[2\]](https://arxiv.org/abs/1803.08463).
- **Hybrid**: We use the joint model for recognizing level-2 entities
and level-1 model for recognizing level-1 entities. This is the method used in the run 2
described in the paper [\[2\]](https://arxiv.org/abs/1803.08463).
- **Separated**: Using level-1 and level-2 model for recognizing level-1
and level-2 entities, respectively. This is the method used in the run 6
described in the paper [\[2\]](https://arxiv.org/abs/1803.08463).

**Evaluation results of the official submissions (See the paper [\[2\]](https://arxiv.org/abs/1803.08463))**

|System | Precision | Recall | F1    |
|--------|-----------|--------|-------|
| **Joint** | 77.99 | 71.1 | **74.70** |
| **Separated** | 78.35 | 70.44 | 74.19 |
| **Hybrid** | 78.32 | 70.88 | 74.41 |

Currently, our **Joint** system obtains SOTA F1 score on VLSP 2018 data set (including nested named entity recognition).

**Note**: the paper Dong and Nguyen, 2018. [Attentive Neural Network for Named Entity Recognition in Vietnamese](https://arxiv.org/abs/1810.13097)
only reported the F1 score for one level of entities not including nested named entities. They did not handle nested named entities.

## Citation

If you use **vietner** in your papers, please cite following papers.


```
@article{minh2018a,
  title={A Feature-Rich Vietnamese Named-Entity Recognition Model},
  author={Minh, Pham Quang Nhat},
  journal={Proceedings of CICLING 2018},
  year={2018}
}
```

```
@article{JCC13163,
    author = {Minh Pham},
    title = {A Feature-Based Model for Nested Named-Entity Recognition at VLSP-2018 NER Evaluation Campaign},
    journal = {Journal of Computer Science and Cybernetics},
    volume = {34},
    number = {4},
    year = {2019},
    keywords = {Nested named-entity recognition, CRF, VLSP},
    abstract = {In this report, we describe our participant named-entity recognition system at VLSP 2018 evaluation campaign. We formalized the task as a sequence labeling problem using BIO encoding scheme. We applied a feature-based model which combines word, word-shape features, Brown-cluster-based features, and word-embedding-based features. We compare several methods to deal with nested entities in the dataset. We showed that combining tags of entities at all levels for training a sequence labeling model (joint-tag model) improved the accuracy of nested named-entity recognition.},
    issn = {1813-9663}, pages = {311--321}, doi = {10.15625/1813-9663/34/4/13163},
    url = {http://www.vjs.ac.vn/index.php/jcc/article/view/13163}
}
```


