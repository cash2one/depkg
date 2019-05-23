#!/usr/bin/env python

import re
import os
import codecs

from argparse import ArgumentParser

PARSER = ArgumentParser(
    description="Tool to extract Node.js executables built with pkg"
)

PARSER.add_argument(
    "-f", "--file",
    required=True,
    help="path to the executable to extract"
)

PARSER.add_argument(
    "-d", "--dest",
    required=True,
    help="path to extract code to"
)

# As far as I can tell, this sequence always appears before the contents of a source file.
MAGIC = b'\xff\xff\xff\xff\x00\x08\x00\x00\x1c'

def findend_handler(error):
    # I haven't been able to locate the  soure file offsets/sizes/metadata yet buried
    # within the packaged executables, so instead we just decode as much UTF8
    # from a starting position as possible, and throw away the error when it
    # hits stuff it shouldn't decode. This should be improved.
    raise Exception(error.start)

def extract(file, dest):
    if not os.path.exists(file):
        print("File does not exist.")
        return False

    try:
        f = open(file, "rb")
        contents = f.read()
    except Exception as e:
        print("Failed to read file. ({})".format(e))
        return False

    try:
        os.makedirs(dest, exist_ok=True)
    except Exception as e:
        print("Failed to create destination directory. ({})".format(e))
        return False

    for i, m in enumerate(re.finditer(MAGIC, contents)):
        start = m.end()

        try:
            str(contents[start:], "utf-8", errors="findend")
        except Exception as e:
            # Horrific hack - see above.
            file = contents[start:start+int(e.args[0])]

        try:
            with open(os.path.join(dest, str(i)), "wb+") as w:
                w.write(file)
        except Exception as e:
            print("Failed to write to output file. ({})".format(e))
            return False

    # Should be truthy so we can get away with returning mixed int/bool values.
    return i

def main():
    codecs.register_error("findend", findend_handler)

    args = PARSER.parse_args()
    result = extract(args.file, args.dest)

    if result:
        print("Extraction to {} completed successfully ({} source files)."
            .format(os.path.abspath(args.dest), result))
    else:
        print("Extraction failed, see error above.")

if __name__ == "__main__":
    main()