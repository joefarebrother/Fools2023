# pylint:disable=wildcard-import,unused-wildcard-import,pointless-string-statement,redefined-outer-name
from disasemble import *
from utils import *

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

useful_vals = {
    "printstr": 0x0008,
    "strcmp": 0x0010,
    "findindex": 0x0018,
    "converthex": 0x0020,
    "memcpy": 0x0028,
    "readstr": 0x0030,
    "strtrim": 0x0038,
    "memset": 0x0040,
    # "breakpoint": 0xFFF0
}

xxops = {x.split()[0] for x in opcode if "$xx" in x and "$xxxx" not in x}
for op in xxops:
    for instr in opcode:
        if instr.startswith(op+" ") and "$xxxx" in instr:
            raise Exception("non-unique opcode with $xx and $xxxx")


for val, name in known_syscalls.items():
    useful_vals[name.lower()] = val


def assemble_file(fname, offset=0x2000):
    return assemble_code(open(fname).readlines(), offset)


def assemble_inline(code, offset=0x2000, as_hex=True):
    res = assemble_code(code.split("/"), offset)
    if as_hex:
        res = "".join(tohex(b) for b in res)
    return res


def instrlen(instr):
    return len(opcode[instr])+("$xxxx" in instr)+("$xx" in instr)


def process_assemble_string(string, labels, dummy=False):
    for m, c, arg in re.findall(r'(\\(F[01])\[(.*?)\])', string, re.MULTILINE):
        arg = arg.replace("$", "0x")
        arg = arg.replace(".", "zx")
        arg = arg.lower()

        ev_arg = 0 if dummy else eval(arg, labels)  # pylint:disable=eval-used
        lo, hi = to_le(ev_arg)

        string = string.replace(m, f"\\x{c}\\x{tohex(lo)}\\x{tohex(hi)}")

    as_bytes = eval("b" + string)  # pylint:disable=eval-used
    return list(as_bytes) + [0]


def assemble_code(lines, offset=0x2000):
    labs = {k: v for k, v in useful_vals.items()}
    instrs = []
    ml_string_assemble_buf = ""

    for ln, line in enumerate(lines):
        try:
            if ml_string_assemble_buf:
                ml_string_assemble_buf += line
                the_str = ml_string_assemble_buf.strip()
                if the_str.endswith('"""'):
                    instrs.append(("ds", the_str))
                    offset += len(process_assemble_string(the_str, None, True))
                    ml_string_assemble_buf = ""
                continue

            if line.strip().startswith('ds '):
                _op, arg = line.split(maxsplit=1)
                sarg = arg.strip()
                if sarg.startswith('"""') and not sarg.endswith('"""'):
                    ml_string_assemble_buf = arg
                    continue
                arg = sarg
                if (comment := arg.find(";")) >= 0:
                    arg = arg[:comment].strip()
                assert arg.startswith('"') and arg.endswith('"')
                instrs.append(("ds", arg))
                offset += len(process_assemble_string(arg, None, True))
                continue

            line = line.replace("$", "0x")
            line = line.replace(".", "zx")
            line = line.lower()

            if (comment := line.find(";")) >= 0:
                line = line[:comment]

            if "=" in line:
                var, val = line.split("=", 1)
                labs[var] = eval(val)  # pylint:disable=eval-used
                continue

            ps = line.split()
            if len(ps) > 0:
                if ps[0][-1] == ":":
                    newlabname = ps.pop(0)[:-1]
                    assert newlabname not in labs, newlabname
                    labs[newlabname] = offset
                    if newlabname.startswith("zx"):
                        labs[newlabname[2:]] = offset
            if len(ps) > 0:
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
                        modps.append("$xx" if modps[0] in xxops else "$xxxx")
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
        if instr == "ds":
            bytesout += process_assemble_string(data, labs)
            continue
        for op in opcode[instr]:
            bytesout.append(op)
        for x in data:
            n = eval(x, labs)  # pylint:disable=eval-used
            bytesout += to_le(n)[:("$xxxx" in instr)+1]
    return bytesout


if __name__ == "__main__":
    if len(sys.argv) > 1:
        fname = sys.argv[1]
        offset = 0x3009
        if len(sys.argv) > 2:
            offset = fromhex(sys.argv)
        s = assemble_file(fname, offset)
        for x in s:
            print(f"{x:0{2}X}", end="")
        print()
    else:
        print("Usage: python3 assemble.py filename [hexoffset [OPTIONS]]")

    # print(assemble("sqrt.prg"),0x3000)
