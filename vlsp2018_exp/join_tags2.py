"""
Join tags of multiple files
"""
from optparse import OptionParser


def read(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return [ l.rstrip() for l in lines ]


def combine(lines1, lines2):
    assert len(lines1) == len(lines2)
    lines = []
    for l1,l2 in zip(lines1,lines2):
        if l1 == "":
            assert l2 == ""
            l = ""
        else:
            fields1 = l1.split()
            fields2 = l2.split()
            assert len(fields1) > 0
            assert len(fields1) == len(fields2)
            for f1,f2 in zip(fields1[:-1], fields2[:-1]):
                assert f1 == f2
            tag = "+".join([fields1[-1], fields2[-1]])
            fields1[-1] = tag
            l = " ".join(fields1)
        lines.append(l)
    return lines


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-o", "--output", dest="output",
                      help = "Path to output file")
    (opt, args) = parser.parse_args()

    if not opt.output:
        parser.error("Path to output is required")
    if len(args) == 0:
        parser.error("Input files are not given")

    output_lines = read(args[0])
    for filename in args[1:]:
        lines = read(filename)
        output_lines = combine(output_lines, lines)

    with open(opt.output, 'w', encoding="utf-8") as fo:
        for line in output_lines:
            fo.write("{}\n".format(line))
