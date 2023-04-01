#pylint: disable=redefined-outer-name



crashes = ['14', '15', '16', '17', '18', '19', '1a', '1b', '1c', '1d', '1e', '1f', 'a0', 'c0', 'c1', 'c2', 'c3', 'c4', 'c6', 'ca', 'cc', 'e4',
           'e5', 'e6', 'e7', 'e8', 'e9', 'ea', 'eb', 'ec', 'ed', 'ee', 'ef', 'f0', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'fa', 'fb', 'fc', 'fd', 'fe', 'ff']

no_args = ['2', '3', '4', '5', '7', '8', '9', 'a', 'c', 'd', 'e', 'f', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '2a', '2b', '2c', '2d', '2e', '2f', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '3a', '3b', '3c', '3d', '3e', '3f', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '4a', '4b', '4c', '4d', '4e', '4f', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '5a', '5b', '5c', '5d', '5e', '5f', '60', '61',
           '62', '63', '64', '65', '66', '67', '68', '69', '6a', '6b', '6c', '6d', '6e', '6f', '70', '71', '72', '73', '74', '75', '76', '77', '78', '79', '7a', '7b', '7c', '7d', '80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '8a', '8b', '8c', '8d', '8e', '8f', '90', '91', '92', '93', '94', '95', '96', '97', 'a6', 'a7', 'a8', 'a9', 'aa', 'ab', 'ac', 'ad', 'ae', 'af', 'd0', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9', 'da', 'db', 'dc', 'dd', 'de', 'df']
one_args = ['06', '7f']
two_args = ['1', 'b', '10', '11', '12', '13', '98', '99', '9a', '9b', '9c', '9d', '9e', '9f', 'a1', 'a2', 'a3', 'a4', 'a5', 'b0', 'b1', 'b2',
            'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'b9', 'ba', 'bb', 'bc', 'bd', 'be', 'bf', 'cd', 'ce', 'cf', 'e0', 'e1', 'e2', 'e3']
three_args = ['7e']
special = ['c5', 'c7', 'c9', 'cb']
no_info = ['c8']

op_lens = {}
for ln, l in enumerate((no_args, one_args, two_args, three_args)):
    for op in l:
        op_lens[int(op, 16)] = ln

crashes = [int(op, 16) for op in crashes]

known_opcodes_pre = {
    0x00: 'BRK',
    0x05: 'ret',
    0x06: 'int $XX',
    0x09: 'ld sp $XXXX',
    0x10: 'ld $R $XXXX',
    0x20: 'ld $RB $RA',
    0x03: 'add $RA $RB',
    0x90: 'push $R',
    0x94: 'pop $R',
    0x98: 'jp $XXXX',
    0x99: 'call $XXXX',
    0x9A: 'jp lt $XXXX',
    0x9B: 'jp gt $XXXX',
    0x9C: 'jp z $XXXX',
    0xA2: 'cmp $R $XXXX',
    0xA7: 'push pc',
    0xb4: 'ld $R [$XXXX]',
    0xbc: 'ld [$XXXX] $R',
    0xe0: 'add $R $XXXX',
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
}
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

maxlen = 0x0360
def disasm(fname="REPORT03.PRG.dump",prog_offset =0x2000):
    dump = open(fname)

    mem = []
    for line in dump:
        addr, memline, chrs = line.split(" | ")
        for b in memline.split():
            b = int(b, 16)
            mem.append(b)

    if maxlen:
        mem = mem[:maxlen]

    pc = 0
    while pc < len(mem):
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
                if argi in known_funcs:
                    op_name = op_name.replace("$XXXX", known_funcs[argi] + f"(${arg})")
                else:
                    op_name = op_name.replace("XXXX", arg)
            elif "$XX" in op_name:
                assert len(args) == 1
                arg = tohex(args[0])
                argi = args[0]
                op_name = op_name.replace("XX", arg)
                if "int" in op_name:
                    op_name += f' ({known_syscalls.get(argi, "unknown")})'
            line += op_name
        elif op in crashes:
            line += "[wait! that's illegal!]"

        pc += 1 + opl
        print(line)
if __name__=="__main__":
    disasm()
