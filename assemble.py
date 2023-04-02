from disasemble import *

"""

label:  ; first token in line ending with colon is considered a label

jp z eval(expr+label)

dw 0000

; comment


todo db
"""

kwds = set()

opcode = {}
for code,op in known_opcodes.items():
    for x in op.split(" "):
        if "$XXXX" not in x and "$XX" not in x:
            kwds.add(x)
    opcode[op] = [code]

opcode["dw"]=[]

def assemble(fname,offset=0x2000):
    lines = list(open(fname))
    labs = {}
    instrs = []

    for ln,line in enumerate(lines):
        try:
            if (comment:=line.find(";"))>=0:
                line=line[:comment]
            ps = line.split()
            if len(ps)>0:
                if ps[0][-1]==":":
                    newlabname = ps.pop(0)[:-1]
                    assert newlabname not in labs
                    labs[newlabname] = offset
            if len(ps)>0:
                if ps[0]=="dw":
                    n = int("".join(ps[1:]),16)
                    instrs.append(("dw",[str(n)]))
                    offset+=2
                else:
                    args = []
                    modps = []
                    for p in ps:
                        if p in kwds:
                            modps.append(p)
                        elif p[0]=="[":
                            assert p[-1]=="]"
                            modps.append("[$XXXX]")
                            args.append(p[1:-1])
                        else:
                            modps.append("$XXXX")
                            args.append(p)
                    print(ps,modps)
                    i = " ".join(modps)
                    if i not in opcode:
                        raise Exception(f"don't recognise {i}")
                    opc = opcode[i][0]
                    instrs.append(opc,args)
                    offset+=op_len(opc)+1
        except Exception as e:
            print(f"failed at line {ln}:{repr(line)}")
            raise e
    bytesout=[]
    for instr,data in instrs:
        for op in opc[instr]:
            bytesout.append(op)
        for x in data:
            n = eval(x,globals=labs)
            bytesout.append(n&255)
            bytesout.append(n>>8)
    return bytesout

if __name__=="__main__":
    print(assemble("asm.txt"))
