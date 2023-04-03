import re
import string


def tohex(num, padding=2):
    if isinstance(num, str):
        num = num.replace(" ", "").replace("\n", "")
        assert re.fullmatch(r'[0-9a-fA-F]+', num)
        return num
    if isinstance(num, list):
        return "".join(tohex(b, padding) for b in num)
    return f"{num:0{padding}X}"


def fromhex(num):
    return int(num, 16)


def to_le(val):
    return [val % 256, val//256]


def from_le(data, offset=0):
    return data[offset+1]*256+data[offset]


def chunks(xs, sz):
    for i in range(0, len(xs), sz):
        yield xs[i:i+sz]


def bytes_from_dump(dump):
    out = []
    if isinstance(dump, str):
        dump = dump.splitlines()
    for line in dump:
        _addr, memline = line.split(" | ", 1)
        if "|" in memline:
            memline = memline.split("|", 1)[0]
        mem = memline.split()
        for b in mem:
            b = fromhex(b)
            out.append(b)
    return out


printable_no_ws = set(string.printable) - set(string.whitespace)


def byte_to_pretty(b):
    c = chr(b)
    if c in printable_no_ws:
        return c
    elif b == 0:
        return " "
    else:
        return "."


def bytes_to_dump(data, addr, chunksize=16):
    out = ""
    for chunk in chunks(data, chunksize):
        memline = " ".join(tohex(c) for c in chunk)
        memline += " " * (23-len(memline))
        chline = "".join(byte_to_pretty(c) for c in chunk)
        out += f"{tohex(addr)} | {memline} | {chline}\n"
        addr += 8
    return out
