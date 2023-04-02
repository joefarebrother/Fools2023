# pylint:disable=wildcard-import,unused-wildcard-import,pointless-string-statement,redefined-outer-name
from disasemble import *

"""

label:  ; first token in line ending with colon is considered a label

jp z eval(expr+label)

dw 0000

; comment


todo db
"""
import sys

kwds = set()

opcode = {}
for code, op in known_opcodes.items():
    op = op.lower()
    for x in op.split(" "):
        if "$xxxx" not in x and "$xx" not in x:
            kwds.add(x)
    opcode[op] = [code]
kwds.add("nop")
kwds.add("dw")
kwds.add("db")
opcode["db $xx"] = []
opcode["dw $xxxx"] = []
opcode["nop"] = [0x20]


def assemble_file(fname, offset=0x2000):
    return assemble_code(open(fname).readlines(), offset)


def assemble_inline(code, offset=0x2000, as_hex=True):
    res = assemble_code(code.split("/"), offset)
    if as_hex:
        res = "".join(tohex(b) for b in res)
    return res

def instrlen(instr):
    return len(opcode[instr])+("$xxxx" in instr)+("$xx" in instr)

def assemble_code(lines, offset=0x2000):
    labs = {}
    instrs = []

    for ln, line in enumerate(lines):
        line = line.replace("$", "0x")
        line = line.replace(".", "zx")
        line = line.lower()
        try:
            if (comment := line.find(";")) >= 0:
                line = line[:comment]
            ps = line.split()
            if len(ps) > 0:
                if ps[0][-1] == ":":
                    newlabname = ps.pop(0)[:-1]
                    assert newlabname not in labs
                    labs[newlabname] = offset
                    if newlabname.startswith("zx"):
                        labs[newlabname[2:]] = offset
            if len(ps) > 0:
                if True:
                    args = []
                    modps = []
                    for p in ps:
                        if p in kwds:
                            modps.append(p)
                        elif p[0] == "[":
                            assert p[-1] == "]"
                            modps.append("[$xxxx]")
                            args.append(p[1:-1])
                        else:
                            modps.append("$xxxx" if "int" not in modps else "$xx")
                            args.append(p)
                    # print(ps,modps,file=sys.stderr)
                    i = " ".join(modps)
                    if i not in opcode:
                        raise Exception(f"don't recognise {i}")
                    instrs.append((i, args))
                    offset += instrlen(i)
        except Exception as e:
            print(f"failed at line {ln}:{repr(line)}", file=sys.stderr)
            raise e
    bytesout = []
    for instr, data in instrs:
        for op in opcode[instr]:
            bytesout.append(op)
        for x in data:
            n = eval(x, labs)  # pylint:disable=eval-used
            bytesout.append(n & 255)
            if "$xxxx" in instr:
                bytesout.append(n >> 8)
    return bytesout


if __name__ == "__main__":
    if len(sys.argv) > 1:
        fname = sys.argv[1]
        offset = 0x3009
        if len(sys.argv) > 2:
            offset = int(sys.argv, 16)
        s = assemble_file(fname, offset)
        for x in s:
            print(f"{x:0{2}X}", end="")
        print()
    else:
        print("Usage: python3 assemble.py filename [hexoffset [OPTIONS]]")

    # print(assemble("sqrt.prg"),0x3000)
