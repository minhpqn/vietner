# -*- coding: utf-8 -*-
"""Extract features for Vietnamese NER
"""
import os
import sys
import re
import pandas as pd
import numpy as np
from argparse import ArgumentParser
from collections import OrderedDict
import regex
from brown import BrownClusters
from w2v import W2VClusters
from gazetteer import Gazetteer
import crfutils
import yaml

class FileFormatError(Exception):
    pass

# Separator of field values.
separator = " "

def read_word_embedding_data(embeddingfile, scale=1.0):
    """Read word embedding data
    Parameters
    -----------
    filepath: String

    Return
    -----------
    word_to_embedding: Dict
       Dictionary that maps word to vectors
    """
    word_to_embedding = {}
    embeddingdim = 0
    print("Reading Embedding file: %s" % embeddingfile)

    with open(embeddingfile) as f:
        for l in f:
            l = l.strip('\n')
            sp = l.split()
            if len(sp) == 2:
                continue

            word_to_embedding[sp[0].lower()] = [float(v)*scale for v in sp[1:]]
            if embeddingdim == 0:
                embeddingdim = len(sp) - 1
            elif embeddingdim != len(sp) - 1:
                raise FileFormatError('Embedding size mismatched: %d # %d' % (embeddingdim, len(sp)-1))

    print('Vector Dimensions = %d' % embeddingdim)
    return word_to_embedding, embeddingdim


def load_embedding_vectors_word2vec(filename, binary=True, scale=1.0):
    # load embedding_vectors from the word2vec
    print("Reading Embedding file: %s" % filename, file = sys.stderr)
    encoding        = 'utf-8'
    embedding_index = {}
    embedding_dim   = 0
    with open(filename, "rb") as f:
        header = f.readline()
        vocab_size, vector_size = map(int, header.split())
        embedding_dim = vector_size
        if binary:
            binary_len = np.dtype('float32').itemsize * vector_size
            for line_no in range(vocab_size):
                word = []
                while True:
                    ch = f.read(1)
                    if ch == b' ':
                        break
                    if ch == b'':
                        raise EOFError("unexpected end of input; is count incorrect or file otherwise damaged?")
                    if ch != b'\n':
                        word.append(ch)
                word = str(b''.join(word), encoding=encoding, errors='strict')
                embedding_index[word] = np.fromstring(f.read(binary_len), dtype='float32')
        else:
            for line_no in range(vocab_size):
                line = f.readline()
                if line == b'':
                    raise EOFError("unexpected end of input; is count incorrect or file otherwise damaged?")
                parts = str(line.rstrip(), encoding=encoding, errors='strict').split(" ")
                if len(parts) != vector_size + 1:
                    raise ValueError("invalid vector on line %s (is this really the text format?)" % (line_no))
                word   = '_'.join(parts[0:len(parts)-embedding_dim])
                vector = []
                for d in parts[-embedding_dim:]:
                    vector.append(np.float32(d))
                embedding_index[word] = vector
        f.close()
        print('Vector Dimensions = %d' % embedding_dim)
        return embedding_index, embedding_dim


def b(v):
    return 'yes' if v else 'no'


def get_shape(token):
    r = ''
    for c in token:
        if c.isupper():
            r += 'U'
        elif c.islower():
            r += 'L'
        elif c.isdigit():
            r += 'D'
        elif c in ('.', ','):
            r += '.'
        elif c in (';', ':', '?', '!'):
            r += ';'
        elif c in ('+', '-', '*', '/', '=', '|', '_'):
            r += '-'
        elif c in ('(', '{', '[', '<'):
            r += '('
        elif c in (')', '}', ']', '>'):
            r += ')'
        else:
            r += c
    return r

def degenerate(src):
    dst = ''
    for c in src:
        if not dst or dst[-1] != c:
            dst += c
    return dst

def get_type(token):
    T = (
        'AllUpper', 'AllDigit', 'AllSymbol',
        'AllUpperDigit', 'AllUpperSymbol', 'AllDigitSymbol',
        'AllUpperDigitSymbol',
        'InitUpper',
        'AllLetter',
        'AllAlnum',
        )
    R = set(T)
    if not token:
        return 'EMPTY'

    for i in range(len(token)):
        c = token[i]
        if c.isupper():
            R.discard('AllDigit')
            R.discard('AllSymbol')
            R.discard('AllDigitSymbol')
        elif c.isdigit() or c in (',', '.'):
            R.discard('AllUpper')
            R.discard('AllSymbol')
            R.discard('AllUpperSymbol')
            R.discard('AllLetter')
        elif c.islower():
            R.discard('AllUpper')
            R.discard('AllDigit')
            R.discard('AllSymbol')
            R.discard('AllUpperDigit')
            R.discard('AllUpperSymbol')
            R.discard('AllDigitSymbol')
            R.discard('AllUpperDigitSymbol')
        else:
            R.discard('AllUpper')
            R.discard('AllDigit')
            R.discard('AllUpperDigit')
            R.discard('AllLetter')
            R.discard('AllAlnum')

        if i == 0 and not c.isupper():
            R.discard('InitUpper')

    for tag in T:
        if tag in R:
            return tag
    return 'NO'

def get_2d(token):
    return len(token) == 2 and token.isdigit()

def get_4d(token):
    return len(token) == 4 and token.isdigit()

def get_da(token):
    bd = False
    ba = False
    for c in token:
        if c.isdigit():
            bd = True
        elif c.isalpha():
            ba = True
        else:
            return False
    return bd and ba

def get_dand(token, p):
    bd = False
    bdd = False
    for c in token:
        if c.isdigit():
            bd = True
        elif c == p:
            bdd = True
        else:
            return False
    return bd and bdd

def get_all_other(token):
    for c in token:
        if c.isalnum():
            return False
    return True

def get_capperiod(token):
    return len(token) == 2 and token[0].isupper() and token[1] == '.'

def contains_upper(token):
    b = False
    for c in token:
        b |= c.isupper()
    return b

def contains_lower(token):
    b = False
    for c in token:
        b |= c.islower()
    return b

def contains_alpha(token):
    b = False
    for c in token:
        b |= c.isalpha()
    return b

def contains_digit(token):
    b = False
    for c in token:
        b |= c.isdigit()
    return b

def contains_symbol(token):
    b = False
    for c in token:
        b |= ~c.isalnum()
    return b

def is_punct(token):
    """Check if token is punctuations
    """
    filters = frozenset([c for c in '!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n'])
    b = False
    _tk = [c for c in token if c not in filters]
    if len(_tk) == 0:
        b = True
    return b

def is_number(token):
    """NUMBER: the token is a number (either real or integer number)
    """
    if re.search(r"^([+-]?([0-9]*)?[0-9]+([.,][0-9]+)*%?$)", token):
        return True
    else:
        return False

def contains_mix_cases(token):
    """is mixed case letters, e.g., “iPhone”
    """
    b = False
    if regex.search(r"\p{Ll}+\p{Lu}+\p{Ll}+", token):
        b = True
    return b

def ends_with_digit(token):
    b = False
    if re.search(r'^[A-Za-z]+\d+$', token):
        b = True
    return b

def is_capitalized(token):
    if regex.search(r"^\p{Lu}(\p{Ll}|_)*$", token):
        return True
    else:
        return False

def isACRONYM(token):
    """Check if a token is an ACRONYM or not
    """
    if regex.search(r"^(\p{Lu}\p{Ll}?\.)+.*$", token):
        return True
    else:
        return False

def contains_hyphen(token):
    """HYPHEN: contains hyphen, such as New-York
    """
    if re.search(r'(\w+-\w)+', token):
        return True
    else:
        return False

def is_date(token):
    """DATE: check if a token is date

    DATE_1 = Pattern.compile("\\b([12][0-9]|3[01]|0*[1-9])[-/.](1[012]|0*[1-9])[-/.](\\d{4}|\\d{2})\\b");
    DATE_2 = Pattern.compile("\\b(1[012]|0*[1-9])[-/.](\\d{4}|\\d{2})\\b");
    DATE_3 = Pattern.compile("\\b([12][0-9]|3[01]|0*[1-9])[-/.](1[012]|0*[1-9])\\b");
    """
    if regex.search(r"^([12][0-9]|3[01]|0*[1-9])[-/.](1[012]|0*[1-9])[-/.](\d{4}|\d{2})$", token) or \
       regex.search(r"^(1[012]|0*[1-9])[-/.](\d{4}|\d{2})$", token) or \
       regex.search(r"^([12][0-9]|3[01]|0*[1-9])[-/.](1[012]|0*[1-9])$", token):

        return True
    else:
        return False

def isName(token):
    """Check if a token is a NAME
       (the first letter of each unit (in case of Vietnamese) is a capital letter)
       For example, Hà_Nội

    Parameter
    ----------
    token: String

    Return
    ----------
    True or False
    """
    all_units = token.split('_')
    if len(all_units) == 0:
        return False
    for u in all_units:
        if u == '' or (not u.isalpha()) or u[0].islower():
            return False
    return True

def isWeight(token):
    if re.search(r"[\+\-]?([0-9]*)?[0-9]+([\.,]\d+)*(Kg|kg|lbs|kilograms|kilogram|kilos|kilo|pounds|pound)", token):
        return True
    else:
        return False

def isCode(token):
    if regex.search(r"^\d+\p{Lu}+$", token):
        return True
    else:
        return False

def _getType(token, word_list):
    w = token.lower()
    if w in word_list:
        return True
    else:
        return False

def isfProvince(token):
    province_words = [
        "tỉnh", "thành_phố", "tp.", "tp",
        "huyện", "quận", "xã", "phường",
        "thị_trấn", "thôn", "bản", "làng",
        "xóm", "ấp",
    ]
    return _getType(token, province_words)

def isfPress(token):
    press_words = [
        "báo", "tờ", "tạp_chí", "đài", "thông_tấn_xã",
    ]
    return _getType(token, press_words)

def isfCommunist(token):
    communist_words = [
        "thành_ủy", "tỉnh_ủy", "quận_ủy",
        "thành_uỷ", "tỉnh_uỷ", "quận_uỷ",
        "huyện_ủy", "xã_ủy", "đảng_ủy",
        "huyện_uỷ", "xã_uỷ", "đảng_uỷ",
    ]
    if token.lower() == "tỉnh_ủy":
        return True
    return _getType(token, communist_words)

def isfPolice(token):
    police_words = [
        "công_an", "cảnh_sát",
    ]
    return _getType(token, police_words)

def isfSchool(token):
    word_list = [
        "ĐH", "CĐ", "THPT", "THCS", "tiểu_học",
    ]
    return _getType(token, word_list)

def isfInstitution(token):
    word_list = [
        "trường", "học_viện", "viện", "institute", "university",
    ]
    return _getType(token, word_list)

def isfCompany(token):
    word_list = [
        "công_ty", "công_ty_cổ_phần",
        "tập_đoàn", "hãng", "xí_nghiệp",
    ]
    return _getType(token, word_list)

def isfUnion(token):
    word_list = [
        "liên_hiệp", "hội", "hợp_tác_xã",
        "câu_lạc_bộ", "trung_tâm", "liên_đoàn", "tổng_liên_đoàn",
    ]
    return _getType(token, word_list)

def isfMilitary(token):
    word_list = [
        "sư_đoàn", "lữ_đoàn", "trung_đoàn", "tiểu_đoàn",
        "quân_khu", "liên_khu",
    ]
    return _getType(token, word_list)

def isfMinistryPrefix(token):
    word_list = [
        "bộ", "ủy_ban",
    ]
    return _getType(token, word_list)

def isfMinistry(token):
    word_list = [
        "chính_trị", "ngoại_giao", "quốc_phòng", "công_an",
        "tư_pháp", "tài_chính", "công_thương", "xây_dựng",
        "nội_vụ", "y_tế", "ngoại_giao", "lao_động", 
        "giao_thông", "thông_tin", "tt", "giáo_dục", "gd",
        "nông_nghiệp", "nn", "kế_hoạch", "kh",   
        "khoa_học", "kh", "văn_hóa", "tài_nguyên", "tn", 
        "dân_tộc",
    ]
    return _getType(token, word_list)

def isfDepartmentPrefix(token):
    word_list = [
        "sở", "phòng", "ban", "chi_cục", "tổng_cục",
    ]
    return _getType(token, word_list)

def isfVillage(token):
    word_list = [
        "quận", "q", "q.", "ấp", "quán", "khu",
        "tổ", "khóm", "xóm", "trạm", "số", "ngách", "ngõ",
    ]
    return _getType(token, word_list)

def isfRegion(token):
    word_list = [
        "bang", "nước", "vùng", "miền",
    ]
    return _getType(token, word_list)

def isfLocPrefix(token):
    word_list = [
        "sông", "núi", "chợ", "châu", 
        "đảo", "đèo", "cầu", "đồi", "đồn", 
        "thủ_đô", "khách_sạn", "sân_bay", "nhà_hàng", "cảng",
        "đường", "phố", "đại_lộ", "chung_cư", "rạch",
        "hồ", "kênh",
    ]
    return _getType(token, word_list)

def isfRoad(token):
    word_list = [
        "tỉnh_lộ", "quốc_lộ",
    ]
    return _getType(token, word_list)

def isfParty(token):
    word_list = [
        "Đảng", "đảng",
    ]
    return _getType(token, word_list)


def disjunctive(X, t, field, begin, end):
    name = '%s[%d..%d]' % (field, begin, end)
    for offset in range(begin, end+1):
        p = t + offset
        if p not in range(0, len(X)):
            continue
        X[t]['F'].append('%s=%s' % (name, X[p][field]))

regexps = OrderedDict({
    # ORG
    "orgAdmin":      ["fAllcaps", "fProvince", "fName"], 
    "orgPress":      ["fPress", "fName"],
    "orgCommunist1": ["fCommunist", "fName"],
    "orgCommunist2": ["fCommunist", "fProvince", "fName"],
    "orgPolice":     ["fPolice", "fProvince", "fName"], 
    "orgSchool1":    ["fSchool", "fName"], 
    "orgSchool2":    ["fInstitution", "fSchool", "fName"],
    "orgSchool3":    ["fName", "fInstitution"],
    "orgCompany":    ["fCompany", "fName"],
    "orgUnion":      ["fUnion", "fName"],
    "orgMilitary":   ["fMilitary", "fNumber"],
    "orgMinistry":   ["fMinistryPrefix", "fMinistry"], 
    "orgDepartment1": ["fDepartmentPrefix", "fMinistry"],
    "orgDepartment2": ["fDepartmentPrefix", "fMinistry", "fProvince", "fName"],
    "orgParty1":     ["fParty", "fName"],
    "orgParty2":     ["fParty", "fCapital", "fName"], 
    "orgParty3":     ["fParty", "fCapital"], 
    # LOC
    "locProvince":   ["fProvince", "fName"], 
    "locVillage":    ["fVillage", "fNumber"],
    "locRegion":     ["fRegion", "fName"],
    "locGeneral":    ["fLocPrefix", "fName"],
    "locRoad1":      ["fRoad", "fCode"],
    "locRoad2":      ["fRoad", "fNumber"],
    "locAddress":    ["fNumber", "fName"],
})

def gen_regex_observation(X):
    """Generate observations based on regular expressions
    """
    for t in range(len(X)):
        X[t]['fNumber']    = is_number(X[t]['w'])
        X[t]['fCapital']   = is_capitalized(X[t]['w'])
        X[t]['fAllcaps']   = X[t]['w'].isupper()
        X[t]['fName']      = isName(X[t]['w']) or X[t]['w'].isupper()
        X[t]['fCode']      = isCode(X[t]['w'])
        X[t]['fProvince']  = isfProvince(X[t]['w'])
        X[t]['fPress']     = isfPress(X[t]['w'])
        X[t]['fCommunist'] = isfCommunist(X[t]['w'])
        X[t]['fPolice']    = isfPolice(X[t]['w'])
        X[t]['fSchool']    = isfSchool(X[t]['w'])
        X[t]['fInstitution'] = isfInstitution(X[t]['w'])
        X[t]['fCompany']   = isfCompany(X[t]['w'])
        X[t]['fUnion']     = isfUnion(X[t]['w'])
        X[t]['fMilitary']  = isfMilitary(X[t]['w'])
        X[t]['fMinistryPrefix'] = isfMinistryPrefix(X[t]['w'])
        X[t]['fMinistry']  = isfMinistry(X[t]['w'])
        X[t]['fDepartmentPrefix'] = isfDepartmentPrefix(X[t]['w'])
        X[t]['fVillage']   = isfVillage(X[t]['w'])
        X[t]['fVillage']   = isfVillage(X[t]['w'])
        X[t]['fRegion']    = isfRegion(X[t]['w'])
        X[t]['fLocPrefix'] = isfLocPrefix(X[t]['w'])
        X[t]['fRoad']      = isfRoad(X[t]['w'])
        X[t]['fParty']     = isfParty(X[t]['w'])

    fRegex = 'fRegex'

    sorted_patterns = sorted(regexps.keys(), key=lambda k: len(regexps[k]), reverse=True)
    marked = [ False for t in range(len(X)) ]
    for t in range(len(X)):
        if X[t].get(fRegex) != None:
            continue

        for pattern in sorted_patterns:
            p = pattern if pattern != 'orgParty3' else 'orgParty2'
            attr_list = regexps[pattern]
            if t + len(attr_list) - 1 >= len(X):
                continue
            
            val = True
            for i in range(len(attr_list)):
                if X[t+i][attr_list[i]] == False:
                    val = False
                    break

            if val == True:
                for i in range(len(attr_list)):
                    X[t+i][fRegex] = p
                break
        if X[t].get(fRegex) == None:
            X[t][fRegex] = 'NA'

def gen_gazetteer_observation(X, gazetteer = None, def_="NA"):
    """Generate Gazetteer Observations
    """
    if gazetteer == None:
        return

    for t in range(len(X)):
        if X[t].get("gz") != None:
            continue

        start_gaze = False
        for offset in range(gazetteer.max_length()+1,0,-1):
            p = t + offset
            if p >= len(X):
                continue

            tokens_ = []
            for i in range(t,p):
                tokens_ += X[i]["w"].split("_")
            value_ = " ".join(tokens_)
            value_ = value_.lower()

            if gazetteer.is_in_gazetteer(value_):
                # print(value_, file=sys.stderr)
                start_gaze = True
                type_ = gazetteer.gazetteer_type(value_)
                for i in range(t,p):
                    X[i]["gz"]  = b( True )
                break

        if not start_gaze:
            X[t]["gz"] = b( False )


def regexp_features(X, t):
    for i in range(-1,1):
        p0 = t + i
        p1 = p0 + 1

        r0 = X[p0]['fRegex'] if p0 > 0 else '__BOS__'
        r1 = X[p1]['fRegex'] if p1 < len(X) else '__EOS__'
        f = 'fRegex[%d]|fRegex[%d]=%s|%s' % (i, i+1, r0, r1)
        X[t]['F'].append(f)

    current_word = X[t]['wl']
    if X[t].get('pos') is not None:
        current_pos = X[t]['pos']
    else:
        current_pos = None
    current_reg  = X[t]['fRegex']
    prev_reg     = X[t-1]['fRegex'] if t-1 > 0 else '__BOS__'
    next_reg     = X[t+1]['fRegex'] if t+1 < len(X) else '__EOS__'

    # w(0) + r(0)
    X[t]['F'].append('w[0]|r[0]=%s|%s' % (current_word,current_reg))
    # w(0) + r[-1]
    X[t]['F'].append('w[0]|r[-1]=%s|%s' % (current_word, prev_reg))
    # w(0) + r[1]
    X[t]['F'].append('w[0]|r[1]=%s|%s' % (current_word, next_reg))

    if current_pos is not None:
        # p(0) + r(0)
        X[t]['F'].append('p[0]|r[0]=%s|%s' % (current_pos, current_reg))
        # p(0) + r(-1)
        X[t]['F'].append('p[0]|r[-1]=%s|%s' % (current_pos, prev_reg))
        # p(0) + r(1)
        X[t]['F'].append('p[0]|r[1]=%s|%s' % (current_pos, next_reg))


def load_config(config_file):
    try:
        with open(config_file, 'r') as ymlfile:
            cfg = yaml.load(ymlfile)
    except IOError as e:
        print(e)
    return cfg


class FeatureExtractor(object):

    def __init__(self, config_file):
        cfg = load_config(config_file)
        self.cfg = cfg

        U = [
            'w', 'wl', 'shape', 'shaped', 'type',
            'p1', 'p2', 'p3', 'p4',
            's1', 's2', 's3', 's4',
            '2d', '4d', 'd&a', 'd&-', 'd&/', 'd&,', 'd&.', 'up',
            'iu', 'au', 'al', 'ad', 'ao',
            'cu', 'cl', 'ca', 'cd', 'cs',
            'mix', 'acr', 'ed', 'hyp', 'da', 'na', 'co', 'wei',
            'fRegex',
            'pos', 'chk',
        ]

        B = [
            'w', 'wl', 'shaped', 'type',
            'fRegex',
            'pos', 'chk',
        ]

        self.fields = cfg['fields']
        self.templates = []

        use_fregex = True
        if cfg.get("use_fregex") is not None:
            use_fregex = cfg.get("use_fregex")
        if not use_fregex:
            print('Drop fregex')
            U.pop(-3)
            B.pop(-3)

        self.use_fregex = use_fregex

        feature_fields = cfg['feature_fields']
        if feature_fields == "w pos":
            U.pop(-1)
            B.pop(-1)
        elif feature_fields == "w":
            U.pop(-1); U.pop(-1)
            B.pop(-1); B.pop(-1)
        elif feature_fields == "w pos chk":
            pass
        else:
            raise ValueError("Invalid feature fields: %s" % feature_fields)

        embedding_name = cfg['word_embeddings']['default']
        if embedding_name is not None:
            binary = cfg['word_embeddings'][embedding_name]['binary']
            word_embedding_data_file = cfg['word_embeddings'][embedding_name]['path']
        else:
            word_embedding_data_file = None
            binary = None

        if word_embedding_data_file is not None and cfg["use_word_embedding"]:
            scale = cfg['word_embeddings']['scale'] if cfg['word_embeddings'].__contains__('scale') else 1.0

            if embedding_name == "glove":
                self.embedding, self.embeddingdim = read_word_embedding_data(word_embedding_data_file, scale = scale)
            elif embedding_name == "word2vec":
                self.embedding, self.embeddingdim = load_embedding_vectors_word2vec(word_embedding_data_file, binary=binary, scale = scale)
            else:
                raise ValueError("Invalid embedding name: %s" % embedding_name)
            self.use_word_embedding = True
            for d in range(self.embeddingdim):
                U.append('em%d' % (d+1))
        else:
            self.use_word_embedding = False
            self.embedding          = {}
            self.embeddingdim       = None

        brown_cluster_config = cfg.get('brown_cluster')
        if brown_cluster_config is not None:
            brown_cluster_data_file = brown_cluster_config['path']
            self.prefix_lengths = [4, 6, 8, 10]
            if brown_cluster_config.get("prefix_lengths") is not None:
                self.prefix_lengths = brown_cluster_config.get("prefix_lengths")
        else:
            brown_cluster_data_file = None

        if brown_cluster_data_file is not None and cfg["use_brown_clusters"]:
            self.brown_clusters     = BrownClusters(brown_cluster_data_file)
            self.use_brown_clusters = True
            U.append('bcb')
            for l in self.prefix_lengths:
                U.append('%dbits' % l)
        else:
            self.brown_clusters     = None
            self.use_brown_clusters = False

        path_to_gazetteer_file = cfg.get("path_to_gazetteer_file")
        if path_to_gazetteer_file != None:
            self.gazetteer = Gazetteer(path_to_gazetteer_file)
            U.append("gz")
            B.append("gz")
        else:
            self.gazetteer = None

        for name in U:
            self.templates += [((name, i),) for i in range(-2, 3)]
        for name in B:
            self.templates += [((name, i), (name, i+1)) for i in range(-2, 2)]

    def crf_options(self):
        return self.cfg["crf_options"]

    def crfpath(self):
        return self.cfg["crfpath"]

    def observation(self, v, defval=''):
        # Lowercased token.
        v['wl'] = v['w'].lower()
        # Token shape.
        v['shape'] = get_shape(v['w'])
        # Token shape degenerated.
        v['shaped'] = degenerate(v['shape'])
        # Token type.
        v['type'] = get_type(v['w'])

        # Prefixes (length between one to four).
        v['p1'] = v['w'][0] if len(v['w']) >= 1 else defval
        v['p2'] = v['w'][:2] if len(v['w']) >= 2 else defval
        v['p3'] = v['w'][:3] if len(v['w']) >= 3 else defval
        v['p4'] = v['w'][:4] if len(v['w']) >= 4 else defval

        # Suffixes (length between one to four).
        v['s1'] = v['w'][-1] if len(v['w']) >= 1 else defval
        v['s2'] = v['w'][-2:] if len(v['w']) >= 2 else defval
        v['s3'] = v['w'][-3:] if len(v['w']) >= 3 else defval
        v['s4'] = v['w'][-4:] if len(v['w']) >= 4 else defval

        # Two digits
        v['2d'] = b(get_2d(v['w']))
        # Four digits.
        v['4d'] = b(get_4d(v['w']))
        # Alphanumeric token.
        v['d&a'] = b(get_da(v['w']))
        # Digits and '-'.
        v['d&-'] = b(get_dand(v['w'], '-'))
        # Digits and '/'.
        v['d&/'] = b(get_dand(v['w'], '/'))
        # Digits and ','.
        v['d&,'] = b(get_dand(v['w'], ','))
        # Digits and '.'.
        v['d&.'] = b(get_dand(v['w'], '.'))
        # A uppercase letter followed by '.'
        v['up'] = b(get_capperiod(v['w']))

        # An initial uppercase letter.
        v['iu'] = b(v['w'] and v['w'][0].isupper())
        # All uppercase letters.
        v['au'] = b(v['w'].isupper())
        # All lowercase letters.
        v['al'] = b(v['w'].islower())
        # All digit letters.
        v['ad'] = b(v['w'].isdigit())
        # All other (non-alphanumeric) letters.
        v['ao'] = b(get_all_other(v['w']))

        # Contains a uppercase letter.
        v['cu'] = b(contains_upper(v['w']))
        # Contains a lowercase letter.
        v['cl'] = b(contains_lower(v['w']))
        # Contains a alphabet letter.
        v['ca'] = b(contains_alpha(v['w']))
        # Contains a digit.
        v['cd'] = b(contains_digit(v['w']))
        # Contains a symbol.
        v['cs'] = b(contains_symbol(v['w']))

        # New features from other papers

        # MIX: is mixed case letters, e.g., “iPhone”
        v['mix'] = b( contains_mix_cases(v['w']) )
        # ACRONYM: e.g., T. or Th.
        v['acr'] = b( isACRONYM(v['w']) )
        # Ends with digit, e.g, A9, B52
        v['ed']  = b( ends_with_digit(v['w']) )
        # HYPHEN: contains hyphen, such as New-York
        v['hyp'] = b( contains_hyphen(v['w']) )
        # DATE: check if a token is date
        v['da']  = b( is_date(v['w']) )
        # is name, where consecutive syllables are capitalized, e.g., “Hà_Nội”, “Buôn_Mê_Thuột”
        v['na']  = b( isName(v['w']) )
        # is code, e.g, “21B”
        v['co']  = b( isCode(v['w']) )
        # is weight
        v['wei'] = b( isWeight(v['w']) )

        if self.use_word_embedding:
            # Word embedding features
            word = v['w'].lower()
            if is_punct(word):
                word = '<punct>'
            elif is_number(word):
                word = '<number>'

            vec = []
            if word not in self.embedding:
                vec = [0.0 for i in range(self.embeddingdim)]
            else:
                vec = self.embedding[word]
            for d in range(len(vec)):
                v['em%d' % (d+1)] = '1:%g' % (vec[d])

        if self.use_brown_clusters:
            word = v['wl']
            bitstring = self.brown_clusters.get_bitchain_of(word, "")
            v['bcb'] = bitstring
            for l in self.prefix_lengths:
                v['%dbits' % l] = bitstring[0:l] if len(bitstring) >= l else ""

    def feature_extractor(self, X):
        # Append observations.
        for x in X:
            self.observation(x)

        gen_regex_observation(X)

        gen_gazetteer_observation(X, gazetteer = self.gazetteer)
        
        # Apply the feature templates.
        crfutils.apply_templates(X, self.templates)

        # Append disjunctive features.
        for t in range(len(X)):
            disjunctive(X, t, 'w', -4, -1)
            disjunctive(X, t, 'w', 1, 4)

            if self.use_fregex:
                regexp_features(X, t)

        # Append BOS and EOS features.
        if X:
            X[0]['F'].append('__BOS__')
            X[-1]['F'].append('__EOS__')

    def extract(self, input_file, output_file):
        fi = open(input_file)
        fo = open(output_file, 'w')

        crfutils.extract_features(self.feature_extractor, 
                                  fields=self.fields,
                                  fi=fi, fo=fo)

        fi.close()
        fo.close()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("config_file", help = "Path to config file",
                        required=True)
    parser.add_argument("input", help = "Path to input file")
    parser.add_argument("output", help = "Path to crfsuite feature file")
    args = parser.parse_args()

    extractor = FeatureExtractor(args.config)
    extractor.extract(args.input, args.output)