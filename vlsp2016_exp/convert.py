"""
Convert data into a realistic scenario
References:
    https://github.com/vncorenlp/VnCoreNLP
"""
import re
import sys
from argparse import ArgumentParser


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
                    fields.pop()
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


parser = ArgumentParser()
parser.add_argument("-i", dest="input", required=True, help="Path to original VLSP 2016 data file")
parser.add_argument("-o", dest="output", required=True, help="Path to converted data file")
args = parser.parse_args()

sentences = load(args.input)
new_sentences = []

for sen in sentences:
    tags = [ tp[-1] for tp in sen ]
    new_sen = []
    i = 0
    while i < len(sen):
        w, pos, chunk, tag = sen[i]
        if is_begin_of_entity(tag) and get_tag(tag) == "PER" and w[0].isupper():
            j = i
            while j < len(sen) and not is_end_of_entity(j, tags):
                j += 1
            is_fullname = True
            for k in range(i,j+1):
                _w, _, _, _ = sen[k]
                if not _w[0].isupper():
                    is_fullname = False
            if is_fullname:
                w_ = "_".join([ tp[0] for tp in sen[i:j+1] ])
                new_sen.append([w_,tag])
                i = j+1
            else:
                new_sen.append([w,tag])
                i += 1
        else:
            new_sen.append([w,tag])
            i += 1
    new_sentences.append(new_sen)

with open(args.output, "w", encoding="utf-8") as fo:
    for sen in new_sentences:
        for w, tag in sen:
            fo.write("{} {}\n".format(w, tag))
        fo.write("\n")




