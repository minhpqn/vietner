# Experiments on VLSP 2018 NER data

Different from VLSP 2016, in VLSP 2018, organizers only provided text documents
with NER tags, there is no word segmentation, POS and chunking info. Therefore,
participant systems need to do preprocessing step before training NER models.

## Requirements

- RDRsegmenter. We modified the vocabulary from the original version of RDRsegmenter. So please
download the modified version [here](https://drive.google.com/open?id=14gleYMl4ECHJklqxZHl8KvyDNv66GZUY).

### Evaluation measures

We use Precision, Recall, F1 scores for entities of all nested levels.
Evaluation measures are calculated by using the official evaluation program
provided by the VLSP 2018 organizer.

### Systems to be compared

- **Joint**: We use joint model to recognize joint tags for each token of
a sequence, then split joint tags into level-1 and level-2 tags. This is the method used in
the run 4 described in the paper [\[2\]](https://arxiv.org/abs/1803.08463).
- **Hybrid**: We use the joint model for recognizing level-2 entities
and level-1 model for recognizing level-1 entities. This is the method used in the run 2
described in the paper [\[2\]](https://arxiv.org/abs/1803.08463).
- **Separated**: Using level-1 and level-2 model for recognizing level-1
and level-2 entities, respectively. This is the method used in the run 6
described in the paper [\[2\]](https://arxiv.org/abs/1803.08463).

## Experimental results

We report results of two experiments:

- **Experiment 1**: we use the provided training data to train the model and
evaluate the trained model on the development set and the test set.

- **Experiment 2**: we combine provided training and development data to make
a new training data to train the model and use that model to evaluate on the test set.
In VLSP 2018 evaluation campaign, we use this method to generate our official submissions.

### Experiment 1

We use the provided training data to train the model and
evaluate the trained model on the development set and the test set.

#### Training

**Create training data**

This shell script will perform word segmentation on the provided training portion,
and create training data for level-1, level-2 and joint model. Format of the training data files
follows CoNLL 2003 format.

    make_exp1_train_data.sh

**Training**

Just run the single shell script `train_exp1_models.sh`. The script will perform following training tasks.

*Training NER Model for level-1 entities*

    python train.py ./config_files/config1.yml ./data/exp1/models/l1_model ./data/exp1/train/train_ws-l1.txt

*Training NER Model for level-2 entities*

    python train.py ./config_files/config1.yml ./data/exp1/models/l2_model ./data/exp1/train/train_ws-l2.txt

*Training NER Model for joint tags*

    python train.py ./config_files/config1.yml ./data/exp1/models/joint_model ./data/exp1/train/train_ws-l1+l2.txt

#### Output generation

Just run the single shell script `gen_exp1_output.sh`. The script will generate NER results on the development and the test set
for three models: **Joint**, **Hybrid**, and **Separated**.

#### Results

We used the official evaluation program which was provided by VLSP 2018 organizer for evaluation.
The program calculated Precision, Recall, F1 scores for all named entities including nested entities.
We only reported overall evaluation without taking *Domains* into account.

Use the program `evaluation.jar` in this current directory for evaluation.

E.g., Evaluate for **Joint** system.

```
java -jar evaluation.jar ./data/VLSP2018-NER-Test-Domains/ ./data/exp1/output/test/joint/
```

**Evaluation results for the experiment 1 on the dev set**

|System | Precision | Recall | F1    |
|--------|-----------|--------|-------|
| **Joint** | 86.17 | 81.84 | 83.95 |
| **Separated** | 87.01 | 81.08 | 83.94 |
| **Hybrid** | 86.86 | 81.64 | 84.17 |

**Evaluation results for the experiment 1 on the test set**

|System | Precision | Recall | F1    |
|--------|-----------|--------|-------|
| **Joint** | 76.98 | 71.1 | **73.92** |
| **Separated** | 76.83 | 69.12 | 72.77 |
| **Hybrid** | 76.81 | 69.58 | 73.02 |

On the test set, the **Joint** system obtained the best F1 score. We see that **Joint** system
consistently obtained better Recall than those of **Separated** and **Hybrid**.

### Experiment 2

We combine provided training and development data to make
a new training data to train the model and use that model to evaluate on the test set.
In VLSP 2018 evaluation campaign, we use this method to generate our official submissions.

Steps are similar as the experiment 1 except that we combine provided training and development
set to make a larger training data for training CRF models. Refer to the script [`run.sh`](./run.sh)
for details.

**Evaluation results of the official submissions (See the paper [\[2\]](https://arxiv.org/abs/1803.08463))**

|System | Precision | Recall | F1    |
|--------|-----------|--------|-------|
| **Joint** | 77.99 | 71.1 | **74.70** |
| **Separated** | 78.35 | 70.44 | 74.19 |
| **Hybrid** | 78.32 | 70.88 | 74.41 |

## Citation

Please cite the following papers when you compare your NER model with
**vietner** on the VLSP 2018 data set in your paper.


```
@article{minh2018a,
  title={A Feature-Rich Vietnamese Named-Entity Recognition Model},
  author={Minh, Pham Quang Nhat},
  journal={Proceedings of CICLING 2018},
  year={2018}
}
```

```
@article{minh2018b,
  title={A Feature-Based Model for Nested Named-Entity Recognition at VLSP-2018 NER Evaluation Campaign},
  author={Minh, Pham Quang Nhat},
  journal={Proceedings of the fifth international workshop on Vietnamese Language and Speech Processing (VLSP 2018)},
  year={2018}
}
```

