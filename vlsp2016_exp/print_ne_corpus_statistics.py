"""Print named-entity corpus statistics 
(number of sentences, number of entities in each type and total)
"""
import re
import sys
from argparse import ArgumentParser
from collections import defaultdict


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


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("input_file", help = "Path to input file (CoNLL format)")
    args = parser.parse_args()

    sentences = load(args.input_file)
    print("# Read %d sentences from %s" % (len(sentences), args.input_file))

    total = 0
    count = defaultdict(int)
    tag_ = None
    beginrow_ = None
    for j,s in enumerate(sentences):
        tags = [ tk[-1] for tk in s ]
        for i,tk in enumerate(s):
            tag = tk[-1]
            row = " ".join(tk)
            if tag == 'O':
                continue
            if is_begin_of_entity(tag):
                tag_ = get_tag(tag)
                beginrow_ = row
            if is_end_of_entity(i, tags):
                checktag_ = get_tag(tag)
                if tag_ is None:
                    raise ValueError("Missing B- tag at row %s\n" % row)
                if checktag_ != tag_:
                    raise ValueError("%s # %s ('%s') at row '%s'\n" % (checktag_, tag_, beginrow_, row))
                count[tag_] += 1
                tag_ = None
    for tg in sorted(count.keys()):
        print("%s\t%d" % (tg, count[tg]))
        total += count[tg]
    print("Total: %d" % total)


                



