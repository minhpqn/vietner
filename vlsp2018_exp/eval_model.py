"""
Evaluate CRF model given input file in CoNLL format
SYNOPSIS:
python eval_model.py [-work_dir <work_dir>] [-config_file <config_file>] <model_file> <test_gold>
"""
import os
import pathlib
from datetime import datetime
import time
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


def time_elapsed(start):
    end = time.time()
    minutes = (end - start) // 60
    secs = (end - start) % 60
    print("Time elapsed {:.2f} min {:.2f} sec.".format(minutes, secs))
    print()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-work_dir", default="./work_dir", help="Path to working directory (save intermediate results)")
    parser.add_argument("-config_file", default="./config_files/config1.yml", help="Path to config file")
    parser.add_argument("-log", required=True, help="Path to log file")
    parser.add_argument("model_file", help="Path to model file")
    parser.add_argument("test_gold", help="Gold standard data (in CoNLL 2003 format with two fields w y)")
    args = parser.parse_args()

    start = time.time()

    pathlib.Path(args.work_dir).mkdir(parents=True, exist_ok=True)

    test_crfsuite_file = os.path.join(args.work_dir, "test.crfsuite")
    test_tag = os.path.join(args.work_dir, "test.tag")
    test_out = os.path.join(args.work_dir, "test.out")
    log_file = args.log

    copy_content(args.config_file, log_file)

    print("Extract features for test data")

    extractor = FeatureExtractor(args.config_file)
    extractor.extract(args.test_gold, test_crfsuite_file)
    time_elapsed(start)

    crfpath = extractor.crfpath()

    print("Tag test data")
    comd = "%s tag -m %s %s > %s" % (crfpath, args.model_file, test_crfsuite_file, test_tag)
    print(comd)
    os.system(comd)

    comd = "paste -d ' ' %s %s > %s" % (args.test_gold, test_tag, test_out)
    print(comd)
    os.system(comd)
    print()

    print("Evaluatation")
    os.system('echo "Test accuracy" >> %s' % log_file)
    os.system('echo "-----------------" >> %s' % log_file)
    comd1 = "./conlleval -d ' ' < %s >> %s" % (test_out, log_file)
    comd2 = "./conlleval -d ' ' < %s" % test_out
    os.system(comd1)
    print(comd2)
    os.system(comd2)
    print()

    end = time.time()
    minutes = (end - start) // 60
    secs = (end - start) % 60
    print("Finished in {:.2f} min {:.2f} sec.".format(minutes, secs))

    os.system('echo "Finished in {:.2f} min {:.2f} sec." >> {:s}'.format(minutes, secs, log_file))




