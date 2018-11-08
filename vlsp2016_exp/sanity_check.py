from argparse import ArgumentParser


def sanity_check(file_path, num_fields, sep=" "):
    assert num_fields > 0
    i = 0
    with open(file_path, "r") as f:
        for line in f:
            i += 1
            line = line.strip()
            if line == '':
                continue
            fields = line.split(sep)
            if len(fields) == num_fields:
                continue
            nfields = len(fields)
            if len(fields) < num_fields:
                raise ValueError("Too few fields at line %d: %s; %d for %d" % (i, line, nfields, num_fields))

            elif len(fields) > num_fields:
                raise ValueError("Too many fields at line %d: %s; %d for %d" % (i, line, nfields, num_fields))


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-tab", action="store_true", help="Use tab as the delimiter")
    parser.add_argument("filename", help="Path to input file")
    parser.add_argument("num_fields", type=int, help="Number of fields in each line")
    args = parser.parse_args()
    if args.tab:
        sep = "\t"
    else:
        sep = " "
    sanity_check(args.filename, args.num_fields, sep)