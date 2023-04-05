import sys
from utils import bytes_from_dump,bytes_to_dump

def read_tables(lines):
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

def dec()

def dump_dec_dump(dec_tab, dmp ):
    bs = bytes_from_dump(dmp)
    dbs = bytes(map(dec_tab.get,bs))
    return bytes_to_dump(dbs,0x2000)


if __name__=="__main__":
    if len(sys.argv)>2:
        t = read_tables(open(sys.argv[1]))[0]
    else:
        print("usage: python3 tables.py ")
