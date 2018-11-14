"""
Evaluate accuracy at each entity level (level-1 and level-2)
"""
from argparse import ArgumentParser
import os
import re
from data_conversion import xml2tokens
from word_segment import preprocess


def read_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    lines = [l.rstrip() for l in lines]
    i = len(lines)-1
    while i > 0 and re.search(r"^[\s\t]*$", lines[i]):
        i -= 1
    return lines[:i+1]


def evaluation(dir_path, test_gold_dir, work_dir):
    filenames = [f for f in os.listdir((dir_path)) if os.path.isfile(os.path.join(dir_path, f))]
    filenames = sorted(filenames)

    dir_path = re.sub(r"/$", "", dir_path)
    test_files = []
    dirname = os.path.basename(dir_path)
    dirs = [d for d in os.listdir(test_gold_dir) if os.path.isdir(os.path.join(test_gold_dir, d))]
    for d in dirs:
        subdir = os.path.join(test_gold_dir, d)
        test_filenames = [f for f in os.listdir((subdir)) if os.path.isfile(os.path.join(subdir, f))]
        for filename in test_filenames:
            file_path = os.path.join(subdir, filename)
            test_files.append(file_path)
    test_files = sorted(test_files, key=lambda x: os.path.basename(x))
    assert len(filenames) == len(test_files)
    assert filenames[1] == os.path.basename(test_files[1])

    l1_out = os.path.join(work_dir, dirname + "-l1.txt")
    l2_out = os.path.join(work_dir, dirname + "-l2.txt")

    fo1 = open(l1_out, "w", encoding="utf-8")
    fo2 = open(l2_out, "w", encoding="utf-8")

    for result_file, test_path in zip(filenames, test_files):
        assert result_file == os.path.basename(test_path)
        result_file_path = os.path.join(dir_path, result_file)
        result_lines = read_file(result_file_path)
        test_lines = read_file(test_path)
        assert len(result_lines) == len(test_lines), "{} {};; {} # {}".format(result_file_path, test_path,
                                                                              len(result_lines), len(test_lines))
        i = 0
        for line1, line2 in zip(result_lines, test_lines):
            i += 1
            line1 = preprocess(line1)
            line2 = preprocess(line2)
            assert bool(line1 == "") == bool(line2 == "")
            if line1 == "":
                continue
            syllables1, _, _ = xml2tokens(line1)
            syllables2, _, _ = xml2tokens(line2)
            if line1 == 'http://vnreview.vn/tu-van-may-tinh/-/view content/content/2392304/vi-sao-ban-dung-dai-dot-mua-laptop-gia-sieu-re':
                continue
            assert syllables1[0][0] == syllables2[0][0], "{} # {} in {} and {} at line {}: {} {}".format(syllables1[0], syllables2[0],
                                                                                 result_file_path, test_path, i, line1, line2)
            assert len(syllables1) == len(syllables2), "'{}'\n'{}'\n{}\n{}\n{}\n{}\n{}\n{}".format(line1, line2, result_file, test_path, len(syllables1), len(syllables2),
                                                                                                   [s[0] for s in syllables1], [s[0] for s in syllables2])
            for syl1, syl2 in zip(syllables1, syllables2):
                fo1.write("{}\n".format(" ".join([ syl1[0], syl1[1], syl2[1] ])))
                fo2.write("{}\n".format(" ".join([ syl1[0], syl1[2], syl2[2] ])))
            fo1.write("\n")
            fo2.write("\n")

    fo1.close()
    fo2.close()

    print("-- level-1 entities --")
    comd = "./conlleval -d ' ' < %s" % l1_out
    print(comd)
    os.system(comd)
    print("----------------------")
    print("-- level-2 entities --")
    comd = "./conlleval -d ' ' < %s" % l2_out
    print(comd)
    os.system(comd)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-work_dir", default="./work_dir", help="Directory to store intermediate results")
    parser.add_argument("output_dir", help="Path to output directory")
    parser.add_argument("gold_dir", help="Path to gold-standard data")
    args = parser.parse_args()
    evaluation(args.output_dir, args.gold_dir, args.work_dir)
