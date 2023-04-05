import sys
from utils import bytes_from_dump,bytes_to_dump
from collections import defaultdict

lns = list(open("ENCTABLE.BIN.dump"))

def read_tables(lines = None):
    if lines is None:
        lines = lns
    bs = bytes_from_dump(lines)
    print(len(bs))
    tables = zip(*(bs[i::256] for i in range(256)))
    res=[]
    for t in tables:
        d = dict(enumerate(t))
        dback = {v:k for k,v in d.items()}
        assert (len(dback)==256)
        res.append((d,dback))
    return res

tabs = read_tables()

def enc1(n):
    return sum(tabs[i][0][n] for i in range(4))&0xFF

decs = defaultdict(list)

for i in range(256):
    decs[enc1(i)].append(i)

if __name__=="__main__":
    if len(sys.argv)>2:
        t = read_tables(open(sys.argv[1]))[0]
    else:
        print("usage: python3 tables.py ")
