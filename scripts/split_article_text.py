import sys
import re

in_file = sys.argv[1]

with open(in_file, "r") as f:
    txt = f.read()

expr = re.compile(r"\.”+")
split = re.sub(r"(\.”?)\s+", r"\1\n", txt)
deduped = re.sub(r"\n+", r"\n", split)

with open(in_file + ".split", "w") as f:
    f.write(deduped)
