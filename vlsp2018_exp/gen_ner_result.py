"""
Generate NER results
SYNOPSIS:
python gen_ner_result.py -config <configFile> -l1_model <l1Model> -l2_model <l2Model> -joint_model <jointModel> <devData> <devOutputDir>

Output:
- Prediction results (with XML tags) for three methods (to directories):
  + Joint
  + Separated
  + Hybrid
"""
import re
import sys
import uuid
import pandas as pd
import pathlib
from argparse import ArgumentParser
from crfsuite_feature import FeatureExtractor
import os
import time
from word_segment import preprocess, get_raw, word_tokenize


def read(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    return [ preprocess(get_raw(l)) for l in lines ]


def time_elapsed(start):
    end = time.time()
    minutes = (end - start) // 60
    secs = (end - start) % 60
    print("Time elapsed {:.2f} min {:.2f} sec.".format(minutes, secs), flush=True)
    print()


def get_sent_tags(sentences, extractor, model_file, tmpdir):
    tmp_input_file = os.path.join(tmpdir, str(uuid.uuid1()) + '.txt')
    test_crfsuite_file = os.path.join(tmpdir, str(uuid.uuid1()) + '.crfsuite')
    tmp_tag_result = os.path.join(tmpdir, str(uuid.uuid1()) + '.tag')

    try:
        with open(tmp_input_file, "w") as fo:
            for words in sentences:
                sequence = [(w.text, "O") for w in words]
                for tp in sequence:
                    fo.write(" ".join(tp))
                    fo.write("\n")
                fo.write("\n")
    except IOError as e:
        print(e)
        os.remove(tmp_input_file)
        sys.exit(1)

    extractor.extract(tmp_input_file, test_crfsuite_file)
    crfpath = extractor.crfpath()

    # Tagging with CRFSuite
    comd = '%s tag -m %s %s > %s' % (crfpath, model_file, test_crfsuite_file, tmp_tag_result)
    # print(comd)
    os.system(comd)

    result_list = []
    try:
        with open(tmp_tag_result) as f:
            cur_sent = []
            for line in f:
                if re.search(r'^[\s\t]*$', line):
                    if len(cur_sent) != 0:
                        result_list.append(cur_sent)
                    cur_sent = []
                else:
                    line = line.strip()
                    cur_sent.append(line)
    except IOError as e:
        print(e)

    if len(cur_sent) != 0:
        result_list.append(cur_sent)

    try:
        os.remove(tmp_input_file)
        os.remove(test_crfsuite_file)
        os.remove(tmp_tag_result)
    except IOError as e:
        print(e)

    return result_list


def is_begin_of_chunk(i, ner_tags):
    b = False
    if ner_tags[i].startswith('B-'):
        b = True
    return b


def is_end_of_chunk(i, ner_tags):
    b = False
    if ner_tags[i] != 'O':
        if i == len(ner_tags) - 1:
            b = True
        elif ner_tags[i+1] == 'O':
            b = True
        elif ner_tags[i+1].startswith('B-'):
            b = True
        else:
            b = False
    return b


def get_tag_name(tag):
    _tag = re.sub(r'B-', '', tag)
    _tag = re.sub(r'I-', '', _tag)
    return _tag


def get_xml_tagged(words, l1_tags, l2_tags, l3_tags=None):
    assert len(words) == len(l1_tags)
    if l2_tags is None:
        l2_tags = ['O' for i in range(len(l1_tags))]
    if l3_tags is None:
        l3_tags = ['O' for i in range(len(l1_tags))]

    out = ""

    end_pos = 0

    in_l1 = False
    in_l2 = False
    in_l3 = False

    for i,w in enumerate(words):
        tag1 = l1_tags[i]
        tag2 = l2_tags[i]
        tag3 = l3_tags[i]
        type1 = get_tag_name(tag1)
        type2 = get_tag_name(tag2)
        type3 = get_tag_name(tag3)
        for j in range(end_pos, w.start):
            out += ' '
        if is_begin_of_chunk(i, l1_tags):
            out += '<ENAMEX TYPE="{}">'.format(type1)
            in_l1 = True
        if is_begin_of_chunk(i, l2_tags) and (not in_l1):
            out += '<ENAMEX TYPE="{}">'.format(type2)
            in_l2 = True
        if is_begin_of_chunk(i, l3_tags) and (not in_l1) and (not in_l2):
            out += '<ENAMEX TYPE="{}">'.format(type3)
            in_l3 = True
        out += w.text2
        if is_end_of_chunk(i, l1_tags) and in_l1:
            out += '</ENAMEX>'
            in_l1 = False
        if is_end_of_chunk(i, l2_tags) and in_l2:
            out += '</ENAMEX>'
            in_l2 = False
        if is_end_of_chunk(i, l3_tags) and in_l3:
            out += '</ENAMEX>'
            in_l3 = False
        end_pos = w.end
    return out


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-config_file", default="./config_files/config1.yml", help="Path to configuration file")
    parser.add_argument("-tmpdir", default="./tmp", help="Path to temporary directory")
    parser.add_argument("-l1_model", required=True, help="Path to l1 model")
    parser.add_argument("-l2_model", required=True, help="Path to l2 model")
    parser.add_argument("-joint_model", required=True, help="Path to joint model")
    parser.add_argument("tokenized_data", help="Path to tokenized data")
    parser.add_argument("test_data_dir", help="Path to test data directory")
    parser.add_argument("output_dir", help="Path to output directory")
    args = parser.parse_args()

    start = time.time()

    joint_out_dir = os.path.join(args.output_dir, "joint")
    sep_out_dir = os.path.join(args.output_dir, "sep")
    hybrid_out_dir = os.path.join(args.output_dir, "hybrid")

    for d in [joint_out_dir, sep_out_dir, hybrid_out_dir]:
        pathlib.Path(d).mkdir(parents=True, exist_ok=True)

    tmpdir = args.tmpdir
    if not os.path.isdir(tmpdir):
        pathlib.Path(tmpdir).mkdir(parents=True, exist_ok=True)

    extractor = FeatureExtractor(args.config_file)

    input_paths = []
    input_files = []
    joint_output_paths = []
    sep_output_paths = []
    hybrid_output_paths = []

    subdirs = [d for d in os.listdir(args.test_data_dir) if os.path.isdir(os.path.join(args.test_data_dir, d))]
    for d in subdirs:
        dd = os.path.join(args.test_data_dir, d)
        files = [f for f in os.listdir(dd) if os.path.isfile(os.path.join(dd, f))]
        for filename in files:
            ff = os.path.join(dd, filename)
            input_paths.append(ff)
            input_files.append(filename)
            joint_output_paths.append(os.path.join(joint_out_dir, filename))
            sep_output_paths.append(os.path.join(sep_out_dir, filename))
            hybrid_output_paths.append(os.path.join(hybrid_out_dir, filename))

    n_files = len(input_files)
    print("# Total input files: {}".format(n_files))

    sent2ws = dict()
    df = pd.read_csv(args.tokenized_data)
    for i in range(len(df)):
        sent = df['raw'][i]
        ws = df['ws'][i]
        sent2ws[sent] = ws

    # Generate output for Joint model
    i = 0
    print_every = 20
    for input_path, joint_output_path, sep_output_path, hybrid_output_path in zip(input_paths, joint_output_paths, sep_output_paths, hybrid_output_paths):
        i += 1
        if i % print_every == 0:
            percent = 100.0 * i / n_files
            print("%s -> %s (%2.f%%)" % (input_path, joint_output_path, percent))
            print("%s -> %s (%2.f%%)" % (input_path, sep_output_path, percent))
            print("%s -> %s (%2.f%%)" % (input_path, hybrid_output_path, percent))
            time_elapsed(start)
        lines = read(input_path)

        sentences = []
        line_id_dict = {}
        sen_id = 0
        for k, line in enumerate(lines):
            if line == "":
                continue
            if line not in sent2ws:
                raise ValueError("{} not found in dict".format(line))
            tokenized_line = sent2ws[line]
            words, _ = word_tokenize(tokenized_line, line)
            sentences.append(words)
            line_id_dict[k] = sen_id
            sen_id += 1
        l1_result = get_sent_tags(sentences, extractor, args.l1_model, tmpdir)
        l2_result = get_sent_tags(sentences, extractor, args.l2_model, tmpdir)
        joint_result = get_sent_tags(sentences, extractor, args.joint_model, tmpdir)
        assert len(joint_result) == len(sentences)
        assert len(l1_result) == len(sentences)
        assert len(l2_result) == len(sentences)
        with open(joint_output_path, "w", encoding="utf-8") as fo:
            for k, line in enumerate(lines):
                if line == "":
                    fo.write("\n")
                    continue
                sen_id = line_id_dict[k]
                words = sentences[sen_id]
                joint_tags = joint_result[sen_id]
                l1_tags = []
                l2_tags = []
                for tag in joint_tags:
                    tag1, tag2 = tag.split('+')
                    l1_tags.append(tag1)
                    l2_tags.append(tag2)
                out = get_xml_tagged(words, l1_tags, l2_tags)
                fo.write("{}\n".format(out))
        # separated model output
        with open(sep_output_path, "w", encoding="utf-8") as fo:
            for k, line in enumerate(lines):
                if line == "":
                    fo.write("\n")
                    continue
                sen_id = line_id_dict[k]
                words = sentences[sen_id]
                l1_tags = l1_result[sen_id]
                l2_tags = l2_result[sen_id]
                out = get_xml_tagged(words, l1_tags, l2_tags)
                fo.write("{}\n".format(out))
        # hybrid model output
        with open(hybrid_output_path, "w", encoding="utf-8") as fo:
            for k, line in enumerate(lines):
                if line == "":
                    fo.write("\n")
                    continue
                sen_id = line_id_dict[k]
                words = sentences[sen_id]
                l1_tags = l1_result[sen_id]
                joint_tags = joint_result[sen_id]
                l2_tags = []
                for tag in joint_tags:
                    tag1, tag2 = tag.split('+')
                    l2_tags.append(tag2)
                out = get_xml_tagged(words, l1_tags, l2_tags)
                fo.write("{}\n".format(out))
