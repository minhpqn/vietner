"""Function for data conversion
"""
import re
import os
from collections import OrderedDict
from nltk.tokenize import WordPunctTokenizer
from argparse import ArgumentParser
# from pyvi.pyvi import ViTokenizer, ViPosTagger


def split_punctuations(words):
    """Split punctuations before and after a words
    """
    tokens = []
    for w in words:
        match = re.match(r'^([\.,!\?;:\(\)\[\]\'\"\s\t\=]*)(.+?)([\.,!\?;:\(\)\[\]\'"\s\t\=]*$)', w)
        punc1 = match.group(1)
        tk = match.group(2)
        punc2 = match.group(3)

        tokens += [ch for ch in punc1]
        tokens.append(tk)
        tokens += [ch for ch in punc2]

    return tokens


# def vi_tokenize(text):
#     text = ViTokenizer.tokenize(text)
#     tlist = text.split()
#
#     i = 0
#     alist = []
#     while i < len(tlist) - 1:
#         if tlist[i + 1].startswith('@') and text.find(tlist[i] + tlist[i + 1]) != -1:
#             alist.append(tlist[i] + tlist[i + 1])
#             i = i + 2
#         else:
#             alist.append(tlist[i])
#             i = i + 1
#     if i == len(tlist) - 1:
#         alist.append(tlist[i])
#
#     return split_punctuations(alist)
#
#
# def vi_pos_tagging(tokens):
#     a = ViPosTagger.postagging(" ".join(tokens))
#     return a[1]


class Syllable(object):

    def __init__(self, text, start, end):
        self.text = text
        self.start = start
        self.end = end

    def __repr__(self):
        return str( (self.text, self.start, self.end) )


class Token(object):

    def __init__(self, _syllables):
        self.syllables = _syllables
        self.text = "_".join([s.text for s in _syllables])
        self.text2 = " ".join([s.text for s in _syllables])
        if len(self.syllables) > 0:
            self.start = self.syllables[0].start
            self.end = self.syllables[-1].end
        else:
            self.start = None
            self.end = None

    def set_syl_indexes(self, start_syl_id, end_syl_id):
        self.start_syl_id = start_syl_id
        self.end_syl_id   = end_syl_id

    def __repr__(self):
        return str( (self.text, self.start_syl_id, self.end_syl_id, self.start, self.end))


def remove_xml_tags(entity):
    entity = re.sub(r"<ENAMEX TYPE=\"(.+?)\">", "", entity)
    entity = re.sub(r"</ENAMEX>", "", entity)
    return entity


def create_syl_index(tokens):
    i = 0
    for tk in tokens:
        start_syl_id = i
        end_syl_id = i + len(tk.syllables)
        tk.set_syl_indexes(start_syl_id, end_syl_id)
        i = end_syl_id


def tokenize(text):
    tokenizer = WordPunctTokenizer()
    syllables = []

    syls = tokenizer.tokenize(text)
    _pos = 0

    for s in syls:
        start = text.find(s, _pos)
        end = start + len(s)
        _pos = end
        syl = Syllable(s, start, end)
        syllables.append(syl)
    return syllables


def depth_level(astring):
    """
    E.g.,
    Tôi là sinh viên -> 0
    ĐHQG <ENAMEX>Hà Nội</ENAMEX> -> 1
    Khoa thanh nhạc <ENAMEX>Học viên âm nhạc <ENAMEX>HCM</ENAMEX></ENAMEX> -> 2
    Args:
        astring: input string with XML tags
    Returns:
        The depth level of a string
    """
    level = 0
    first = True
    first_add_child = True
    OPEN_TAG = 1
    stack = []
    i = 0
    while i < len(astring):
        # print(astring[i:], stack, level)
        if astring[i:].startswith("<ENAMEX TYPE="):
            if first:
                level += 1
                first = False
            if len(stack) > 0:
                if first_add_child:
                    level += 1
                    first_add_child = False
            stack.append(OPEN_TAG)
            i += len("<ENAMEX TYPE=")
        elif astring[i:].startswith("</ENAMEX>"):
            stack.pop()
            i += len("</ENAMEX>")
        else:
            i += 1
    return level


def get_entities(line):
    """

    Args:
        line (string): Input sentence (single sentence) with XML tags
        E.g., Đây là lý do khiến <ENAMEX TYPE=\"PERSON\">Yoon Ah</ENAMEX> quyết định cắt mái tóc dài 'nữ thần'

    Returns:
        raw (string): raw sentence
        entities (list): list of entities (json object) (Wit.ai)
    """
    debug = False
    raw = ""
    entities = []

    regex_opentag = re.compile(r"<ENAMEX TYPE=\"(.+?)\">")
    regex_closetag = re.compile(r"</ENAMEX>")
    next_start_pos = 0
    match1 = regex_opentag.search(line, next_start_pos)
    stack = []
    if match1:
        raw += line[0:match1.start()]
        next_start_pos = match1.end()
        stack.append(match1)
    else:
        raw = line

    while len(stack) != 0:
        if debug: print("#Current stack", stack)
        match1 = stack.pop()
        if debug: print("#From next_start_pos {}: {}".format(next_start_pos, line[next_start_pos:]))
        next_closetag1 = regex_closetag.search(line, next_start_pos)
        if not next_closetag1:
            raise ValueError("Close tag not found")
        next_end_pos1 = next_closetag1.start()
        match2 = regex_opentag.search(line, next_start_pos, next_end_pos1)
        if match2:
            raw += line[next_start_pos:match2.start()]
            next_start_pos1 = match2.end()
            next_closetag2 = regex_closetag.search(line, next_start_pos1)
            if not next_closetag2:
                raise ValueError("Close tag not found")
            next_end_pos2 = next_closetag2.start()
            match3 = regex_opentag.search(line, next_start_pos1, next_end_pos2)
            if match3:
                level = 1
                raw += line[next_start_pos1:match3.start()]
                next_start_pos2 = match3.end()
                value = line[next_start_pos2:next_end_pos2]
                _type = match3.group(1)

                entity = OrderedDict()
                entity["type"] = _type
                entity["value"] = value
                entity["start"] = len(raw)
                entity["end"] = entity["start"] + len(value)
                entity["level"] = level
                entities.append(entity)

                if debug: print("#Entity:", value, _type, level)
                raw += value
                next_start_pos = next_closetag2.end()
                stack.append(match1)
                stack.append(match2)
            else:
                # Get entity between match2 and next_closetag2
                value = remove_xml_tags( line[match2.end():next_end_pos2] )
                _type = match2.group(1)
                # abc <ENAMEX> xyz <ENAMEX>dhg</ENAMEX> mpq</ENAMEX> r
                level = 1 + depth_level( line[match2.end():next_end_pos2] )
                if debug: print("#current: ", raw)
                raw += line[next_start_pos1:next_closetag2.start()]
                if debug: print("->", raw)
                entity = OrderedDict()
                entity["type"] = _type
                entity["value"] = value
                entity["start"] = len(raw) - len(value)
                entity["end"] = len(raw)
                entity["level"] = level
                entities.append(entity)

                if debug: print("#Entity:", value, _type, level)
                next_start_pos = next_closetag2.end()
                stack.append(match1)
                next_match2 = regex_opentag.search(line, next_start_pos)
                next_closetag3 = regex_closetag.search(line, next_start_pos)

                if next_match2:
                    if next_closetag3 and next_match2.start() < next_closetag3.start():
                        if debug: print("Next match2:", line[next_match2.start():])
                        if debug: print("#current: ", raw)
                        raw += line[next_start_pos:next_match2.start()]
                        if debug: print("->", raw)
                        next_start_pos = next_match2.end()
                        stack.append(next_match2)
        else:
            # Get entity between match1 and next_closetag1
            value = remove_xml_tags( line[match1.end():next_closetag1.start()] )
            _type = match1.group(1)
            level = 1 + depth_level( line[match1.end():next_closetag1.start()] )
            if debug: print("#current: ", raw)
            raw += line[next_start_pos:next_closetag1.start()]
            if debug: print("->", raw)
            entity = OrderedDict()
            entity["type"] = _type
            entity["value"] = value
            entity["start"] = len(raw) - len(value)
            entity["end"] = len(raw)
            entity["level"] = level
            entities.append(entity)
            if debug: print("#Entity:", value, _type, level)
            next_start_pos = next_closetag1.end()

            next_match1 = regex_opentag.search(line, next_start_pos)
            next_closetag3 = regex_closetag.search(line, next_start_pos)
            if next_match1:
                if next_closetag3 and next_match1.start() < next_closetag3.start():
                    if debug: print("#Next match1:", line[next_match1.start():])
                    if debug: print("#current: ", raw)
                    raw += line[next_start_pos:next_match1.start()]
                    if debug: print("->", raw)
                    next_start_pos = next_match1.end()
                    stack.append(next_match1)
                else:
                    continue
            else:
                if debug: print("#current: ", raw)
                if debug: print("{} {}".format(next_closetag1.end(), line[next_closetag1.end():]))
                if not re.search(r"</ENAMEX>", line[next_closetag1.end():]):
                    raw += line[next_closetag1.end():]
                    if debug: print("->", raw)

    return raw, entities



def find_syl_index(start, end, syllables):
    """Find start and end indexes of syllables
    """
    start_syl_id = None
    end_syl_id   = None
    for i, syl in enumerate(syllables):
        if syl.start == start:
            start_syl_id = i
        if syl.end == end:
            end_syl_id = i+1

        if i > 0 and syl.start >= start and syllables[i-1].end <= start:
            start_syl_id = i
        if i == 0 and syl.start > start:
            start_syl_id = i

        if i < len(syllables)-1 and syl.end < end and syllables[i+1].start > end:
            end_syl_id = i+1

        if syl.end >= end and syl.start < end:
            end_syl_id = i+1
        if i == len(syllables)-1 and syl.end <= end:
            end_syl_id = i+1

        if i > 0 and syl.start < start and syllables[i-1].end < start:
            start_syl_id = i

        if syl.start < start and syl.end >= end:
            start_syl_id = i
            end_syl_id = i + 1

        if i == 0 and len(syllables) > 0 and syl.start < start and syl.end < end:
            start_syl_id = i

    if start_syl_id == None:
        print("Cannot find start_syl_id '{}' (end={}) in '{}'".format(start, end, syllables))
    if end_syl_id == None:
        print("Cannot find end_syl_id '{}' (start={}) in '{}'".format(end, start, syllables))

    return start_syl_id, end_syl_id


def find_tok_index(start_syl_id, end_syl_id, tokens):
    start_tok_id = None
    end_tok_id   = None

    for i,tk in enumerate(tokens):
        if tk.start_syl_id == start_syl_id:
            start_tok_id = i
        if tk.end_syl_id == end_syl_id:
            end_tok_id = i+1
    return start_tok_id, end_tok_id


def xml2tokens(xml_tagged_sent):
    """Convert XML-based tagged sentence into CoNLL format based on syllables
    Args:
        xml_tagged_sent (string): Input sentence (single sentence) with XML tags

    Returns:
        tokens (list): list of tuples (tk, level1_tag, level2_tag)
          level1_tag is entity tag (BIO scheme) at the level 1
          level2_tag is entity tag at the level 2 (nested entity)
    """
    raw, entities = get_entities(xml_tagged_sent)
    if re.search(r"ENAMEX", raw):
        print(xml_tagged_sent)
        print(raw)
        # count += 1

    syllables = tokenize(raw)
    level1_syl_tags = ["O" for i in range(len(syllables))]
    level2_syl_tags = ["O" for i in range(len(syllables))]
    level3_syl_tags = ["O" for i in range(len(syllables))]

    flag = False
    for entity in entities:
        value = entity["value"]
        start = entity["start"]
        end = entity["end"]
        entity_type = entity["type"]
        start_syl_id, end_syl_id = find_syl_index(start, end, syllables)

        if start_syl_id != None and end_syl_id != None:
            if entity["level"] == 1:
                level1_syl_tags[start_syl_id] = "B-" + entity_type
                for i in range(start_syl_id + 1, end_syl_id):
                    level1_syl_tags[i] = "I-" + entity_type
            elif entity["level"] == 2:
                level2_syl_tags[start_syl_id] = "B-" + entity_type
                for i in range(start_syl_id + 1, end_syl_id):
                    level2_syl_tags[i] = "I-" + entity_type
            else:
                level3_syl_tags[start_syl_id] = "B-" + entity_type
                for i in range(start_syl_id + 1, end_syl_id):
                    level3_syl_tags[i] = "I-" + entity_type
        else:
            print("{},{},\"{}\" in '{}' ({})".format(start,end,value,raw,xml_tagged_sent))
            flag = True

    ret_syllables = list(zip([ s.text for s in syllables], level1_syl_tags, level2_syl_tags, level3_syl_tags))
    return ret_syllables, raw, flag


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("data_dir", help = "Path to data directory")
    parser.add_argument("syl_output", help = "Path to output file based on syllables")
    args = parser.parse_args()

    subdirs = [ d for d in os.listdir(args.data_dir) if os.path.isdir(os.path.join(args.data_dir,d)) ]
    fo1 = open(args.syl_output, "w", encoding="utf-8")

    for d in subdirs:
        dd = os.path.join(args.data_dir, d)
        files = [ f for f in os.listdir(dd) if os.path.isfile(os.path.join(dd,f)) ]
        for filename in files:
            ff = os.path.join(dd, filename)
            with open(ff, "r") as f:
                for line in f:
                    line = line.strip()
                    line = line.strip(u"\ufeff")
                    line = line.strip(u"\u200b\u200b\u200b\u200b\u200b\u200b\u200b")
                    if line == "":
                        continue
                    if re.search(r"^_*$", line):
                        continue
                    syllables, _, flag = xml2tokens(line)
                    raw_ = "".join([s[0] for s in syllables])
                    if raw_ == "":
                        print(ff, line)
                    if flag:
                        print("File: {}".format(ff))
                        print()
                    for tp in syllables:
                        fo1.write("{}\n".format(" ".join(tp)))
                    fo1.write("\n")
    fo1.close()



