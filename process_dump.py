# pylint:disable=wildcard-import,unused-wildcard-import
import string
from utils import *

printable_no_ws = set(string.printable) - set(string.whitespace)

file = "memory-e000-ffff"
dump = open(file).readlines()

processed = ""

for line in dump:
    addr, memline = line.split(" | ")
    mem = memline.split()
    chrs = ""
    for b in mem:
        b = fromhex(b)
        if chr(b) in printable_no_ws:
            chrs += chr(b)
        elif b == 0:
            chrs += " "
        else:
            chrs += "."

    processed += f"{addr} | {memline.strip()} | {chrs}\n"
    #print(processed, end="")

open(file+"-proc", "w").write(processed)
