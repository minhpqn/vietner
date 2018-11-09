"""
Word Segmentation by RDRsegmenter
https://github.com/datquocnguyen/RDRsegmenter
"""
import re
import unittest
import os
import pathlib
from argparse import ArgumentParser
from data_conversion import Syllable, Token, find_syl_index, find_tok_index
from data_conversion2 import get_entities


def text_normalize(text):
    """
    Chuẩn hóa dấu tiếng Việt
    """

    text = re.sub(r"òa", "oà", text)
    text = re.sub(r"óa", "oá", text)
    text = re.sub(r"ỏa", "oả", text)
    text = re.sub(r"õa", "oã", text)
    text = re.sub(r"ọa", "oạ", text)
    text = re.sub(r"òe", "oè", text)
    text = re.sub(r"óe", "oé", text)
    text = re.sub(r"ỏe", "oẻ", text)
    text = re.sub(r"õe", "oẽ", text)
    text = re.sub(r"ọe", "oẹ", text)
    text = re.sub(r"ùy", "uỳ", text)
    text = re.sub(r"úy", "uý", text)
    text = re.sub(r"ủy", "uỷ", text)
    text = re.sub(r"ũy", "uỹ", text)
    text = re.sub(r"ụy", "uỵ", text)
    text = re.sub(r"Ủy", "Uỷ", text)

    return text


def preprocess(text):
    text = text.strip()
    text = text.strip(u"\ufeff")
    text = text.strip(u"\u200b\u200b\u200b\u200b\u200b\u200b\u200b")
    text = text_normalize(text)
    return text


def get_raw(line):
    regex_opentag = re.compile(r"<ENAMEX TYPE=\"(.+?)\">")
    regex_closetag = re.compile(r"</ENAMEX>")
    text = regex_opentag.sub("",line)
    text = regex_closetag.sub("", text)
    return text


def is_end_of_sentence(i, line):
    exception_list = [
        "Mr.",
        "MR.",
        "GS.",
        "Gs.",
        "PGS.",
        "Pgs.",
        "pgs.",
        "TS.",
        "Ts.",
        "ts.",
        "MRS.",
        "Mrs.",
        "mrs.",
        "Tp.",
        "tp.",
        "Kts.",
        "kts.",
        "BS.",
        "Bs.",
        "Co.",
        "Ths.",
        "MS.",
        "Ms.",
        "TT.",
        "TP.",
        "tp.",
        "ĐH.",
        "Corp.",
        "Dr.",
        "Prof.",
        "BT.",
        "Ltd.",
        "P.",
        "MISS.",
        "miss.",
        "TBT.",
        "Q.",
    ]
    if i == len(line)-1:
        return True

    if line[i+1] != " ":
        return False

    if i < len(line)-2 and line[i+2].islower():
        return False

    if re.search(r"^(\d+|[A-Za-z])\.", line[:i+1]):
        return False

    for w in exception_list:
        pattern = re.compile("%s$" % w)
        if pattern.search(line[:i+1]):
            return False

    return True


def is_valid_xml(astring):
    """Check well-formed XML"""
    if not re.search(r"<ENAMEX TYPE=\"(.+?)\">", astring):
        return True

    OPEN_TAG = 1
    stack = []
    i = 0
    while i < len(astring):
        # print(astring[i:], stack, level)
        if astring[i:].startswith("<ENAMEX TYPE="):
            stack.append(OPEN_TAG)
            i += len("<ENAMEX TYPE=")
        elif astring[i:].startswith("</ENAMEX>"):
            if len(stack) > 0:
                stack.pop()
            else:
                # raise ValueError(astring)
                print("Invalid XML format: %s" % astring)
                return False
            i += len("</ENAMEX>")
        else:
            i += 1
    if len(stack) > 0:
        return False
    else:
        return True


def sent_tokenize(line):
    """Do sentence tokenization by using regular expression"""
    sentences = []
    cur_pos = 0
    if not re.search(r"\.", line):
        return [line]

    for match in re.finditer(r"\.", line):
        _pos = match.start()
        end_pos = match.end()
        if is_end_of_sentence(_pos, line):
            tmpsent = line[cur_pos:end_pos]
            tmpsent = tmpsent.strip()
            if is_valid_xml(tmpsent):
                cur_pos = end_pos
                sentences.append(tmpsent)

    if len(sentences) == 0:
        sentences.append(line)
    elif cur_pos < len(line)-1:
        sentences.append(line[cur_pos+1:])
    return sentences


def create_syl_index(tokens):
    i = 0
    for tk in tokens:
        start_syl_id = i
        end_syl_id = i + len(tk.syllables)
        tk.set_syl_indexes(start_syl_id, end_syl_id)
        i = end_syl_id


def word_tokenize(text, raw_text):
    tokens = []
    syllables = []

    words = text.split()

    _pos = 0
    for w in words:
        syls = []
        _syls = w.split("_")
        _syls = [s for s in _syls if s != ""]
        for s in _syls:
            start = raw_text.find(s, _pos)
            end = start + len(s)
            _pos = end
            syl = Syllable(s, start, end)
            syls.append(syl)
            syllables.append(syl)
        token = Token(syls)
        tokens.append(token)
    create_syl_index(tokens)
    return tokens, syllables


def read(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return [ l.rstrip() for l in lines ]


def xml2tokens(xml_tagged_sent, tokenized_sent, raw_sent):
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

    tokens, syllables = word_tokenize(tokenized_sent, raw_sent)
    level1_syl_tags = ["O" for i in range(len(syllables))]
    level2_syl_tags = ["O" for i in range(len(syllables))]
    level3_syl_tags = ["O" for i in range(len(syllables))]

    level1_token_tags = ["O" for i in range(len(tokens))]
    level2_token_tags = ["O" for i in range(len(tokens))]
    level3_token_tags = ["O" for i in range(len(tokens))]

    flag = False
    for entity in entities:
        value = entity["value"]
        start = entity["start"]
        end = entity["end"]
        entity_type = entity["type"]
        start_syl_id, end_syl_id = find_syl_index(start, end, syllables)
        start_tok_id, end_tok_id = find_tok_index(start_syl_id, end_syl_id, tokens)

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

        if start_tok_id != None and end_tok_id != None:
            if entity["level"] == 1:
                level1_token_tags[start_tok_id] = "B-" + entity_type
                for i in range(start_tok_id+1, end_tok_id):
                    level1_token_tags[i] = "I-" + entity_type
            elif entity["level"] == 2:
                level2_token_tags[start_tok_id] = "B-" + entity_type
                for i in range(start_tok_id + 1, end_tok_id):
                    level2_token_tags[i] = "I-" + entity_type
            else:
                level3_token_tags[start_tok_id] = "B-" + entity_type
                for i in range(start_tok_id + 1, end_tok_id):
                    level3_token_tags[i] = "I-" + entity_type
        else:
            pass
            # print("{},{},\"{}\" in '{}' ({})".format(start_syl_id, end_syl_id, value, raw, xml_tagged_sent))

    ret_syllables = list(zip([ s.text for s in syllables], level1_syl_tags, level2_syl_tags, level3_syl_tags))
    ret_tokens = list(zip( [tk.text for tk in tokens], level1_token_tags, level2_token_tags, level3_token_tags))
    return ret_syllables, ret_tokens, raw, flag


class WordSegmentTest(unittest.TestCase):

    def test_xml2tokens(self):
        xml_sent = 'Ở một diễn biến khác, <ENAMEX TYPE="ORGANIZATION">Marseille</ENAMEX> đã đã xoáy <ENAMEX TYPE="ORGANIZATION">PSG</ENAMEX> trên Twitter về vụ tranh giành penalty của <ENAMEX TYPE="PERSON">Neymar</ENAMEX> và <ENAMEX TYPE="PERSON">Cavani</ENAMEX>. <ENAMEX TYPE="ORGANIZATION">Marseille</ENAMEX> đá đểu bằng cách đăng tấm ảnh chụp hai cầu thủ và viết: “Va chạm ở <ENAMEX TYPE="ORGANIZATION">OM</ENAMEX>'
        tokenized_sent = 'Ở một diễn_biến khác , Marseille đã đã xoáy PSG trên Twitter về vụ tranh_giành penalty của Neymar và Cavani . Marseille đá đểu bằng cách đăng tấm ảnh chụp hai cầu_thủ và viết : “ Va_chạm ở OM'
        raw_sent = 'Ở một diễn biến khác, Marseille đã đã xoáy PSG trên Twitter về vụ tranh giành penalty của Neymar và Cavani. Marseille đá đểu bằng cách đăng tấm ảnh chụp hai cầu thủ và viết: “Va chạm ở OM'
        tokens, syllables, _, _ = xml2tokens(xml_sent, tokenized_sent, raw_sent)
        print(tokens)
        print(syllables)

        xml_sent = 'Đối tượng là <ENAMEX TYPE="PERSON">Nguyễn Trường Giang</ENAMEX> (SN 1990, ngụ <ENAMEX TYPE="LOCATION">ấp Bình Thủy</ENAMEX>, <ENAMEX TYPE="LOCATION">xã Hòa khánh Đông</ENAMEX>, <ENAMEX TYPE="LOCATION">huyện Đức Hòa</ENAMEX>). Đối tượng còn lại chạy thoát vào khu dừa nước ra <ENAMEX TYPE="LOCATION">kênh An Hạ</ENAMEX>, lực lượng chức năng đang tích cực truy tìm.'
        tokenized_sent = 'Đối_tượng là Nguyễn_Trường_Giang ( SN 1990 , ngụ ấp Bình_Thuỷ , xã Hoà khánh Đông , huyện Đức_Hoà ) . Đối_tượng còn lại chạy thoát vào khu dừa_nước ra kênh An_Hạ , lực_lượng chức_năng đang tích_cực truy_tìm .'
        raw_sent = 'Đối tượng là Nguyễn Trường Giang (SN 1990, ngụ ấp Bình Thủy, xã Hòa khánh Đông, huyện Đức Hòa). Đối tượng còn lại chạy thoát vào khu dừa nước ra kênh An Hạ, lực lượng chức năng đang tích cực truy tìm.'
        tokens, syllables, _, _ = xml2tokens(xml_sent, tokenized_sent, raw_sent)
        print(tokens)
        print(syllables)

    def test_sent_tokenize(self):
        xml_line = 'Đối tượng là <ENAMEX TYPE="PERSON">Nguyễn Trường Giang</ENAMEX> (SN 1990, ngụ <ENAMEX TYPE="LOCATION">ấp Bình Thủy</ENAMEX>, <ENAMEX TYPE="LOCATION">xã Hòa khánh Đông</ENAMEX>, <ENAMEX TYPE="LOCATION">huyện Đức Hòa</ENAMEX>). Đối tượng còn lại chạy thoát vào khu dừa nước ra <ENAMEX TYPE="LOCATION">kênh An Hạ</ENAMEX>, lực lượng chức năng đang tích cực truy tìm.'
        for sent in sent_tokenize(xml_line):
            print(sent)

        line = "Mr. Minh là sinh viên"
        self.assertFalse(is_end_of_sentence(2,line))
        print(sent_tokenize(line))

        astring = 'Đối tượng là <ENAMEX TYPE="PERSON">Nguyễn Trường'
        self.assertFalse(is_valid_xml(astring))
        self.assertTrue(xml_line)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--sent_tokenize", action="store_true")
    parser.add_argument("--tmpdir", default="./work_dir")
    parser.add_argument("data_dir")
    parser.add_argument("syllable_out")
    parser.add_argument("ws_out")
    args = parser.parse_args()

    print("# Data directory: {}".format(args.data_dir))
    print("# Temporary directory: {}".format(args.tmpdir))
    tmpdir = args.tmpdir
    pathlib.Path(tmpdir).mkdir(exist_ok=True, parents=True)
    dirname = os.path.basename(args.data_dir).split("/")[-1]
    raw_text = os.path.join(tmpdir, dirname + "-raw.txt")
    xml_text = os.path.join(tmpdir, dirname + "-xml.txt")
    subdirs = [d for d in os.listdir(args.data_dir) if os.path.isdir(os.path.join(args.data_dir, d))]
    fo1 = open(raw_text, "w", encoding="utf-8")
    fo2 = open(xml_text, "w", encoding="utf-8")
    for d in subdirs:
        dd = os.path.join(args.data_dir, d)
        files = [f for f in os.listdir(dd) if os.path.isfile(os.path.join(dd, f))]
        for filename in files:
            ff = os.path.join(dd, filename)
            with open(ff, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    line = line.strip(u"\ufeff")
                    line = line.strip(u"\u200b\u200b\u200b\u200b\u200b\u200b\u200b")
                    line = text_normalize(line)
                    if line == "":
                        continue
                    if args.sent_tokenize:
                        sentences = sent_tokenize(line)
                        for s in sentences:
                            raw = get_raw(s)
                            fo1.write("%s\n" % raw)
                            fo2.write("%s\n" % s)
                    else:
                        raw = get_raw(line)
                        fo1.write("%s\n" % raw)
                        fo2.write("%s\n" % line)
    fo1.close()
    fo2.close()

    # Do word-segmentation
    comd = "./word_segment.sh %s" % raw_text
    print(comd)
    os.system(comd)

    tokenized_file = raw_text + ".WS"
    raw_lines = read(raw_text)
    xml_lines = read(xml_text)
    tokenized_lines = read(tokenized_file)
    assert len(xml_lines) == len(tokenized_lines)
    assert len(xml_lines) == len(raw_lines)

    fo1 = open(args.syllable_out, "w", encoding="utf-8")
    fo2 = open(args.ws_out, "w", encoding="utf-8")
    for xml_sent, tokenized_sent, raw_sent in zip(xml_lines, tokenized_lines, raw_lines):
        syllables, tokens, _, _ = xml2tokens(xml_sent, tokenized_sent, raw_sent)
        raw_ = "".join([s[0] for s in syllables])
        if raw_ == "":
            print(xml_sent)
            continue
        for tp in syllables:
            fo1.write("{}\n".format(" ".join(tp)))
        fo1.write("\n")
        for tp in tokens:
            fo2.write("{}\n".format(" ".join(tp)))
        fo2.write("\n")
    fo1.close()
    fo2.close()


