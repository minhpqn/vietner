"""
A miscellaneous utility for sequential labeling.
Copyright 2010,2011 Naoaki Okazaki.
"""
import re
import sys

def apply_templates(X, templates):
    """
    Generate features for an item sequence by applying feature templates.
    A feature template consists of a tuple of (name, offset) pairs,
    where name and offset specify a field name and offset from which
    the template extracts a feature value. Generated features are stored
    in the 'F' field of each item in the sequence.

    @type   X:      list of mapping objects
    @param  X:      The item sequence.
    @type   template:   tuple of (str, int)
    @param  template:   The feature template.
    """
    
    for template in templates:
        name = '|'.join(['%s[%d]' % (f, o) for f, o in template])
        for t in range(len(X)):
            values = []
            for field, offset in template:

                p = t + offset
                if p not in range(len(X)):
                    values = []
                    break
                values.append(X[p][field])
            if values:
                X[t]['F'].append('%s=%s' % (name, '|'.join(values)))

def readiter(fi, names, sep=' '):
    """
    Return an iterator for item sequences read from a file object.
    This function reads a sequence from a file object L{fi}, and
    yields the sequence as a list of mapping objects. Each line
    (item) from the file object is split by the separator character
    L{sep}. Separated values of the item are named by L{names},
    and stored in a mapping object. Every item has a field 'F' that
    is reserved for storing features.

    @type   fi:     file
    @param  fi:     The file object.
    @type   names:  tuple
    @param  names:  The list of field names.
    @type   sep:    str
    @param  sep:    The separator character.
    @rtype          list of mapping objects
    @return         An iterator for sequences.
    """
    X = []
    
    i = 0
    prev_line = ''
    for line in fi:
        i += 1
        line = line.strip('\n')
        if not line:
            yield X
            X = []
        else:
            fields = line.split()
            if len(fields) < len(names):
                raise ValueError(
                    'Too few fields (%d) for %r\n at line: "%s"; line number %d (prev_line: "%s")' % (len(fields), names, line, i, prev_line))
            item = {'F': []}    # 'F' is reserved for features.
            for i in range(len(names)):
                item[names[i]] = fields[i]
            X.append(item)
            prev_line = line

def escape(src):
    """
    Escape colon characters from feature names.

    @type   src:    str
    @param  src:    A feature name
    @rtype          str
    @return         The feature name escaped.
    """
    return src.replace(':', '__COLON__')

def output_features(fo, X, field=''):
    """
    Output features (and reference labels) of a sequence in CRFSuite
    format. For each item in the sequence, this function writes a
    reference label (if L{field} is a non-empty string) and features.

    @type   fo:     file
    @param  fo:     The file object.
    @type   X:      list of mapping objects
    @param  X:      The sequence.
    @type   field:  str
    @param  field:  The field name of reference labels.
    """
    for t in range(len(X)):
        if field:
            fo.write('%s' % X[t][field])
        for a in X[t]['F']:
            if isinstance(a, str):
                if re.search(r'^em', a):
                    fo.write('\t%s' % a)
                else:
                    fo.write('\t%s' % escape(a))
            else:
                fo.write('\t%s:%f' % (escape(a[0]), a[1]))
        fo.write('\n')
    fo.write('\n')

def to_crfsuite(X):
    """
    Convert an item sequence into an object compatible with crfsuite
    Python module.

    @type   X:      list of mapping objects
    @param  X:      The sequence.
    @rtype          crfsuite.ItemSequence
    @return        The same sequence in crfsuite.ItemSequence type.
    """
    import crfsuite
    xseq = crfsuite.ItemSequence()
    for x in X:
        item = crfsuite.Item()
        for f in x['F']:
            if isinstance(f, str):
                item.append(crfsuite.Attribute(escape(f)))
            else:
                item.append(crfsuite.Attribute(escape(f[0]), f[1]))
        xseq.append(item)
    return xseq

def extract_features(feature_extractor, fields='w pos y', sep=' ', **kwargs):
    fi = kwargs.get('fi')
    fo = kwargs.get('fo')
    if fi == None:
        fi = sys.stdin
    if fo == None:
        fo = sys.stdout

    F = fields.split(' ')
    for X in readiter(fi, F, sep):
        feature_extractor(X)
        output_features(fo, X, 'y')