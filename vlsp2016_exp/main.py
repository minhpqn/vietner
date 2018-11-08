"""Main script for experiments
"""
import os
import pathlib
import time
from datetime import datetime
from argparse import ArgumentParser
from crfsuite_feature import FeatureExtractor


def copy_content(input_file, output_file):
    with open(input_file) as fi:
        content = fi.read()
        with open(output_file, 'w') as fo:
            fo.write('Experiments at %s\n' % str(datetime.now()))
            fo.write('-------------------\n')
            fo.write('Experiment config\n')
            fo.write('-------------------\n')
            fo.write('%s\n' % content)
            fo.write('---- End of config ----\n')
            fo.write('\n')


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-no_extract", action="store_true", help="Do not do feature extraction")
    parser.add_argument("-tab", action="store_true", help="Use tab as delimiter character in data files")
    parser.add_argument("config_file", help = "Path to config file")
    parser.add_argument("exp_dir", help = "Path to experiment dir")
    parser.add_argument("training_file", help = "Path to training data")
    parser.add_argument("test_file", help = "Path to test file")
    args = parser.parse_args()

    START = time.time()

    if not os.path.isdir(args.exp_dir):
        pathlib.Path(args.exp_dir).mkdir(parents=True, exist_ok=True)

    training_crfsuite_file = os.path.join(args.exp_dir, "train.crfsuite")
    training_tag = os.path.join(args.exp_dir, "train.tag")
    training_out = os.path.join(args.exp_dir, "train.out")
    model_file = os.path.join(args.exp_dir, "model.bin")

    test_crfsuite_file = os.path.join(args.exp_dir, "test.crfsuite")
    test_tag = os.path.join(args.exp_dir, "test.tag")
    test_out = os.path.join(args.exp_dir, "test.out")
    log_file = os.path.join(args.exp_dir, "log.txt")

    copy_content(args.config_file, log_file)

    os.system('echo "Training data file: %s" >> %s' % (args.training_file, log_file))
    os.system('echo "Test data file: %s" >> %s' % (args.test_file, log_file))
    os.system('echo "-----------------" >> %s' % log_file)

    extractor = FeatureExtractor(args.config_file)
    if not args.no_extract:
        print("Step 1: Extract features for training data")
        start = time.time()
        extractor.extract(args.training_file, training_crfsuite_file)
        end = time.time()
        minutes = (end - start) // 60
        secs = (end - start) % 60
        print("Finished in {:.2f} min {:.2f} sec.".format(minutes, secs), flush=True)
        print()

    crfpath = extractor.crfpath()
    print("Step 2: Training CRF model")
    start = time.time()
    comd = "%s learn %s -m %s %s" % ( crfpath, extractor.crf_options(), model_file, training_crfsuite_file)
    print(comd)
    os.system(comd)
    end = time.time()
    minutes = (end - start) // 60
    secs = (end - start) % 60
    print("Finished in {:.2f} min {:.2f} sec.".format(minutes, secs), flush=True)
    print()

    print("Step 3: Tag training data")
    comd = "%s tag -m %s %s > %s" % (crfpath, model_file, training_crfsuite_file, training_tag)
    print(comd)
    os.system(comd)
    if args.tab:
        comd = "paste %s %s > %s" % (args.training_file, training_tag, training_out)
    else:
        comd = "paste -d ' ' %s %s > %s" % (args.training_file, training_tag, training_out)
    print(comd)
    os.system(comd)
    print()

    if not args.no_extract:
        print("Step 4: Extract features for test data")
        start = time.time()
        extractor.extract(args.test_file, test_crfsuite_file)
        end = time.time()
        minutes = (end - start) // 60
        secs = (end - start) % 60
        print("Finished in {:.2f} min {:.2f} sec.".format(minutes, secs), flush=True)
        print()

    print("Step 5: Tag test data")
    comd = "%s tag -m %s %s > %s" % (crfpath, model_file, test_crfsuite_file, test_tag)
    print(comd)
    os.system(comd)
    if args.tab:
        comd = "paste %s %s > %s" % (args.test_file, test_tag, test_out)
    else:
        comd = "paste -d ' ' %s %s > %s" % (args.test_file, test_tag, test_out)
    print(comd)
    os.system(comd)
    print()

    print("Step 6: Evaluatation")
    print("# Evaluation on training data")
    os.system('echo "Training accuracy" >> %s' % log_file)
    os.system('echo "-----------------" >> %s' % log_file)
    if args.tab:
        comd1 = "./conlleval -d '\\t' < %s >> %s" % (training_out, log_file)
        comd2 = "./conlleval -d '\\t' < %s" % training_out
    else:
        comd1 = "./conlleval -d ' ' < %s >> %s" % (training_out, log_file)
        comd2 = "./conlleval -d ' ' < %s" % training_out
    os.system(comd1)
    print(comd2)
    os.system(comd2)
    print()
    print("# Evaluation on test data")

    os.system('echo "Test accuracy" >> %s' % log_file)
    os.system('echo "-----------------" >> %s' % log_file)
    if args.tab:
        comd1 = "./conlleval -d '\\t' < %s >> %s" % (test_out, log_file)
        comd2 = "./conlleval -d '\\t' < %s" % test_out
    else:
        comd1 = "./conlleval -d ' ' < %s >> %s" % (test_out, log_file)
        comd2 = "./conlleval -d ' ' < %s" % test_out
    os.system(comd1)
    print(comd2)
    os.system(comd2)
    print()

    END = time.time()
    minutes = (END - START) // 60
    secs = (END - START) % 60
    print("Finished in {:.2f} min {:.2f} sec.".format(minutes, secs), flush=True)

    os.system('echo "Finished in {:.2f} min {:.2f} sec." >> {:s}'.format(minutes, secs, log_file))
