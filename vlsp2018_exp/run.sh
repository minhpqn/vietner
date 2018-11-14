#!/bin/sh

# The shell scrip to generate output of three systems
# Joint, Separated, and Hybrid

# Generate training and test data for the experiment 2

sh make_exp2_data.sh

# Train models in the experiment 2

sh train_exp2_models.sh

# Generate output for the experiment 2

sh gen_exp2_output.sh

# Evaluation: Please run following command line to evaluate systems

# Joint system
# java -jar evaluation.jar ./data/VLSP2018-NER-Test-Domains/ ./data/exp2/output/test/joint/

# Separated system
# java -jar evaluation.jar ./data/VLSP2018-NER-Test-Domains/ ./data/exp2/output/test/sep/

# Hybrid system
# java -jar evaluation.jar ./data/VLSP2018-NER-Test-Domains/ ./data/exp2/output/test/hybrid/