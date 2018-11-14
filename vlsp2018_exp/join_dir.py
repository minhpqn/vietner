import os
import sys
import pathlib


train_dir = "./data/VLSP2018-NER-train-Jan14"
dev_dir = "./data/VLSP2018-NER-dev"

args = sys.argv[1:]

if len(args) == 0:
    print("Output dir is not given")
    sys.exit(1)

out_dir = args[0]

if not os.path.isdir(out_dir):
    pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)

comd = "cp -r %s/* %s" % (train_dir, out_dir)
print(comd)
os.system(comd)

comd = "cp -r %s/* %s" % (dev_dir, out_dir)
print(comd)
os.system(comd)




