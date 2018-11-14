"""
Split nested results returned by main.py and evaluate on each level
SYNOPSIS:
$ python split_nested_result.py result_file
"""
import os
import sys
import time
from argparse import ArgumentParser


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("result_file", help = "Nested result file")
    args = parser.parse_args()

    if not os.path.isfile(args.result_file):
        print("File {} does not exist".format(args.result_file))
        sys.exit(1)

    START = time.time()

    print("Step 1: Split result file into two files")
    result_l1 = args.result_file + ".l1"
    result_l2 = args.result_file + ".l2"

    with open(args.result_file, "r") as fi:
        f1 = open(result_l1, "w")
        f2 = open(result_l2, "w")

        for line in fi:
            line = line.rstrip()
            if line == "":
                f1.write("\n")
                f2.write("\n")
                continue

            w, itag, otag = line.split()
            l1_itag, l2_itag = itag.split("+")
            l1_otag, l2_otag = otag.split("+")
            f1.write("{}\n".format(" ".join([w, l1_itag, l1_otag])))
            f2.write("{}\n".format(" ".join([w, l2_itag, l2_otag])))
        f1.close()
        f2.close()

    print("Step 2: Evaluation")
    print("# Level 1 entity (file: {})".format(result_l1))
    comd = "./conlleval -d ' ' < %s" % result_l1
    print(comd)
    os.system(comd)
    print("# Level 2 entity (file: {})".format(result_l2))
    comd = "./conlleval -d ' ' < %s" % result_l2
    print(comd)
    os.system(comd)

    END = time.time()
    minutes = (END - START) // 60
    secs = (END - START) % 60
    print("Finished in {:.2f} min {:.2f} sec.".format(minutes, secs), flush=True)
