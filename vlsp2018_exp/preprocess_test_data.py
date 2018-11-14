"""
Preprocessing test data
"""
import re
from argparse import ArgumentParser
import os
from word_segment import get_raw, preprocess, read
import pandas as pd
import csv

parser = ArgumentParser()
parser.add_argument("-tmpdir", default="./work_dir", help="Path to temporary files")
parser.add_argument("test_data_dir", help="Path to test directory")
parser.add_argument("output_file", help="Path to output preprocessed file")
args = parser.parse_args()

test_data_dir = re.sub(r"/$", "", args.test_data_dir)
dirname = os.path.basename(test_data_dir).split("/")[-1]
raw_text = os.path.join(args.tmpdir, dirname + "-raw.txt")

fo = open(raw_text, "w", encoding="utf-8")

subdirs = [d for d in os.listdir(args.test_data_dir) if os.path.isdir(os.path.join(args.test_data_dir, d))]
for d in subdirs:
    dd = os.path.join(args.test_data_dir, d)
    files = [f for f in os.listdir(dd) if os.path.isfile(os.path.join(dd, f))]
    for filename in files:
        ff = os.path.join(dd, filename)
        with open(ff, "r") as f:
            for line in f:
                line = preprocess(get_raw(line))
                if line == "":
                    continue
                fo.write("%s\n" % line)
fo.close()

# Do word-segmentation
comd = "./word_segment.sh %s" % raw_text
print(comd)
os.system(comd)

raw_tokenized_file = raw_text + ".WS"
raw_lines = read(raw_text)
tokenized_lines = read(raw_tokenized_file)
assert len(raw_lines) == len(tokenized_lines)

df1 = pd.DataFrame(data={'raw': raw_lines, 'ws': tokenized_lines}, columns=['raw','ws'])
df1.to_csv(args.output_file, quoting=csv.QUOTE_ALL)

