#pylint: disable=redefined-outer-name
import re
import sys

crashes = ['14', '15', '16', '17', '18', '19', '1a', '1b', '1c', '1d', '1e', '1f', 'c0', 'c1', 'c2', 'c3', 'c4', 'c6', 'e4',
           'e5', 'e6', 'e7', 'e8', 'e9', 'ea', 'eb', 'ec', 'ed', 'ee', 'ef', 'f0', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'fa', 'fb', 'fc', 'fd', 'fe', 'ff']

crashes = [int(op, 16) for op in crashes]

known_opcodes_pre = {
    0x00: 'BRK',
    0x01: 'mul R0 $XXXX',
    0x05: 'ret',
    0x06: 'int $XX',
    0x09: 'ld sp $XXXX',
    0x0A: 'ld R0 sp',
    0x0E: 'shl R0',
    0x0F: 'shr R0',
    0x10: 'ld $R $XXXX',
    0x20: 'ld $RB $RA',
    0x30: 'add $RB $RA',
    0x40: 'ldb $RB [$RA]',
    0x50: 'ld $RB [$RA]',
    0x60: 'ldb [$RB] $RA',
    0x70: 'ld [$RB] $RA',
    0x90: 'push $R',
    0x94: 'pop $R',
    0x98: 'jp $XXXX',
    0x99: 'call $XXXX',
    0x9A: 'jp lt $XXXX',
    0x9B: 'jp gt $XXXX',
    0x9C: 'jp eq $XXXX',
    0x9D: 'jp ne $XXXX',
    0x9E: 'call lt $XXXX',
    0x9F: 'call gt $XXXX',
    0xA0: 'call eq $XXXX',
    0xA1: 'call ne $XXXX',
    0xA2: 'cmp $R $XXXX',
    0xA6: 'push sp',
    0xA7: 'push pc',
    0xA8: 'inc $R',
    0xAC: 'dec $R',
    0xB0: 'ldb $R [$XXXX]',
    0xB4: 'ld $R [$XXXX]',
    0xB8: 'ldb [$XXXX] $R',
    0xBC: 'ld [$XXXX] $R',
    0xD8: 'xor R0 $R',
    0xDC: 'swap R0',
    0xE0: 'add $R $XXXX',
    0xC5: 'jp $R',
    0xC9: 'call $R',
    0xCD: 'and R0 $XXXX',
    0xCE: 'or R0 $XXXX',
    0xCF: 'xor R0 $XXXX',
}

known_opcodes = {}
for k, v in known_opcodes_pre.items():
    if "$R" in v:
        if "$RA" in v and "$RB" in v:
            for rb in range(4):
                for ra in range(4):
                    idx = rb*4+ra
                    known_opcodes[k+idx] = v.replace("$RA", f"R{ra}").replace("$RB", f"R{rb}")
        else:
            # assert k % 4 == 0
            for r in range(4):
                known_opcodes[k+r] = v.replace("$R", f"R{r}")
    else:
        known_opcodes[k] = v

known_syscalls = {
    0x01: "out",
    0x02: "in",
    0x03: "halt",
    0x04: "load_blk",
    0x05: "rand",
}

op_lens = {6: 1}


def op_len(op):
    return op_lens.get(op, 0)


for k, v in known_opcodes.items():
    if "$XXXX" in v and op_len(k) == 0:
        op_lens[k] = 2

known_funcs = {
    0x0008: "PrintStr  ",
    0x0010: "StrCmp    ",
    0x0018: "FindIndex ",
    0x0020: "ConvertHex",
    0x0028: "MemCpy    ",
    0x0030: "ReadStr   ",
    0x0038: "StrTrim   ",
    0x0040: "MemSet    ",
}


def tohex(n, pad=2):
    return f"{n:0{pad}X}"


def as_le(args):
    assert len(args) == 2, args
    return tohex(args[1]) + tohex(args[0])
# dump = open("MATHTEST.PRG.dump")
# prog_offset = 0x2000
# maxlen = 0

# dump = open("memory-part.dump")
# prog_offset = 0xF000
# maxlen = 0


def process_string(mem, pc):
    the_escaped_str = ""
    while pc < len(mem):
        ch = mem[pc]
        pc += 1
        if ch == 0:
            break
        if ch < 128:
            ch = chr(ch)
            if ch == '\\':
                the_escaped_str += "\\\\"
            elif ch == '\n':
                the_escaped_str += "\\n"
            else:
                the_escaped_str += ch
        else:
            if ch in [0xF0, 0xF1]:
                loc = tohex(mem[pc+1]) + tohex(mem[pc])
                pc += 2
                the_escaped_str += f"\\{tohex(ch)}[${loc}]"
            else:
                the_escaped_str += "\\" + tohex(ch)
    return pc, the_escaped_str


def disasm(fname="REPORT03.PRG.dump", prog_offset=0x2000, maxlen=0x360):
    dump = open(fname)
    out = []
    jump_locs = []
    str_locs = []
    str_vals = {}

    mem = []
    for line in dump:
        _addr, memline, _chrs = line.split(" | ")
        for b in memline.split():
            b = int(b, 16)
            mem.append(b)

    if maxlen:
        mem = mem[:maxlen]

    pc = 0
    while pc < len(mem):
        line = ""
        line += tohex(prog_offset + pc, 4) + " | "

        if pc+prog_offset in str_locs:
            npc, str_val = process_string(mem, pc)
            str_vals[pc+prog_offset] = str_val
            strlen = npc - pc
            for i in range(strlen):
                line += tohex(mem[pc+i]) + " "
            line += " |\n    ds \""
            line += str_val
            line += '"'

            pc = npc
            out.append(line)
            continue
        op = mem[pc]
        opl = op_len(op)
        assert opl+pc <= len(mem)
        args = []
        for i in range(opl):
            args.append(mem[pc+1+i])

        line = ""
        line += tohex(prog_offset + pc, 4) + " | "
        line += tohex(op)
        for a in args:
            line += " " + tohex(a)

        line += " "*(16-len(line)) + "| "

        if op in known_opcodes:
            op_name = known_opcodes[op]
            if "$XXXX" in op_name:
                arg = as_le(args)
                argi = int(arg, 16)
                if "call" in op_name or "jp" in op_name:
                    if argi in known_funcs:
                        op_name = op_name.replace("$XXXX", known_funcs[argi] + f"; (${arg})")
                        if "PrintStr" in known_funcs[argi]:
                            for l in reversed(out):
                                if "R2" in l:
                                    m = re.findall(r'(add|ld) R2 \$(.{4})', l)
                                    if not m:
                                        break
                                    pr_op, pr_arg = m[0]
                                    pr_arg = int(pr_arg, 16)
                                    strloc = pr_arg if pr_op == "ld" else pr_arg + prog_offset
                                    str_locs.append(strloc)
                                    break

                    else:
                        op_name = op_name.replace("XXXX", arg)
                    if prog_offset <= argi < prog_offset+len(mem):
                        jump_locs.append(argi)
                else:
                    op_name = op_name.replace("XXXX", arg)
            elif "$XX" in op_name:
                assert len(args) == 1
                arg = tohex(args[0])
                argi = args[0]
                op_name = op_name.replace("XX", arg)
                if "int" in op_name:
                    op_name += f'  ; ({known_syscalls.get(argi, "unknown")})'
            line += op_name
        elif op in crashes:
            line += "[wait! that's illegal!]"

        pc += 1 + opl
        out.append(line)

    labels = {}

    for line in open("labels.sym"):
        ctx, addr, lab = line.split(":", 2)
        if fname.startswith(ctx):
            labels[int(addr, 16)] = lab.strip()

    for i, loc in enumerate(jump_locs):
        if loc not in labels:
            lab = f".lab_{i}_{tohex(loc)}"
            labels[loc] = lab

    for i, loc in enumerate(str_locs):
        if loc not in labels:
            summary = ""
            if loc in str_vals:
                str_val = str_vals[loc]
                words = re.split(r'[^A-Za-z0-9]', str_val)
                for w in words:
                    if w:
                        summary = "_" + w
                        break
            lab = f".str_{i}_{tohex(loc)}{summary}"
            labels[loc] = lab

    for line in out:
        addr, rest = line.split(" | ", 1)
        addri = int(addr, 16)
        if addri in labels:
            print(labels[addri] + ":")
        for loc, lab in labels.items():
            loch = tohex(loc)
            if "$"+loch in rest:
                rest = rest.replace("$"+loch, lab)
                rest += f" ; (${loch})"

        if ";" in rest:
            code, comment = rest.split(";", 1)
            rest = code + " "*(40-len(code)) + ";" + comment
        print(f"{addr} | {rest}")


if __name__ == "__main__":
    argc = len(sys.argv)
    if argc == 1:
        disasm()
        exit()
    filename = sys.argv[1]
    offset = int(sys.argv[2], 16) if argc >= 3 else 0x2000
    max_size = int(sys.argv[3], 16) if argc >= 4 else 0x360
    disasm(filename, offset, max_size)
