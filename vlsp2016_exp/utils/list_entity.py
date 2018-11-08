"""
List all entities in the data
"""
import re
import sys
from argparse import ArgumentParser


parser = ArgumentParser()
parser.add_argument("-type", required=True, help="Named-entity type")
parser.add_argument("-input", required=True, help="Path to input data")
parser.add_argument("output", help="Path to output file")
args = parser.parse_args()


def load(input_file):
    """Load file in CoNLL format to list of token list
    """
    sentences = []
    i = 0
    with open(input_file) as f:
        cur_sent = []
        for line in f:
            i += 1
            line = line.rstrip()
            if re.search(r'^[\s\t]*$', line):
                if len(cur_sent) != 0:
                    sentences.append(cur_sent)
                cur_sent = []
            else:
                try:
                    fields = line.split()
                    if fields[-1] == "O_" or fields[-1] == "0" or fields[-1] == "o":
                        print("Line {}".format(i))
                except ValueError as e:
                    print(e, "Line at %d: %s" % (i,line))
                    sys.exit(1)
                cur_sent.append(fields)

    return sentences


def is_begin_of_entity(tag):
    if tag.startswith('B-'):
        b = True
    else:
        b = False
    return b


def is_end_of_entity(i, tags):
    b = False
    if tags[i] != 'O':
        if i == len(tags) - 1:
            b = True
        elif tags[i+1] == 'O' or tags[i+1].startswith('B-'):
            b = True
        else:
            b = False
    return b


def get_tag(tag):
    tag_ = tag
    tag_ = re.sub(r"^(B|I)-", "", tag_)
    return tag_


sentences = load(args.input)
entity = dict()
for sen in sentences:
    tags = [tp[-1] for tp in sen]
    i = 0
    while i < len(sen):
        w = sen[i][0]
        tag = sen[i][-1]
        if is_begin_of_entity(tag) and get_tag(tag) == args.type:
            j = i
            while j < len(sen) and not is_end_of_entity(j, tags):
                j += 1
            w_ = " ".join([tp[0] for tp in sen[i:j + 1]])
            entity[w_] = 1
            i = j+1
        else:
            i += 1

with open(args.output, "w") as fo:
    for e in sorted( entity.keys() ):
        fo.write("{}\n".format(e))

