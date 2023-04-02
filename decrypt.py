# pylint:disable=global-statement

encrypted_data_dump = r"""
1160 | FB 72 3A 22 21 4B 6A C2 | .r:"!Kj.
1168 | 28 E6 E4 C1 A7 25 B6 E0 | (....%..
1170 | 98 B2 0A E0 9B AB C1 84 | ........
1178 | B8 2D 8F D8 7E 07 3A CB | .-..~.:.
1180 | C9 F0 F5 38 51 43 ED 52 | ...8QC.R
1188 | F8 44 E4 C2 50 22 27 2A | .D..P"'*
1190 | 65 44 81 79 C2 6C B4 AF | eD.y.l..
1198 | D9 9D 7C 74 B3 58 EA CD | ..|t.X..
11A0 | 69 E2 A2 DF E7 CA C4 65 | i......e
11A8 | E0 E8 F3 BE EE 97 68 AD | ......h.
11B0 | 61 0E 27 78 32 86 6D 5C | a.'x2.m\
11B8 | 02 C2 6E D1 DF 93 14 4D | ..n....M
11C0 | CB 1A 90 F4 20 95 C0 D3 | ........
11C8 | 1D E8 73 2B DB AF AE 74 | ..s+...t
11D0 | 7A 1D 50 4A A6 9D 56 CC | z.PJ..V.
11D8 | B5 5D 07 D1 04 A7 16 5C | .].....\
11E0 | 1D 40 4E 65 51 F2 68 0A | .@NeQ.h.
11E8 | 4A B3 56 56 C1 51 1F 0F | J.VV.Q..
11F0 | C2 7D 4B 29 5B 58 1D 2F | .}K)[X./
11F8 | FF 66 C0 3C BB BB 34 93 | .f.<..4.
1200 | 30 E6 34 B7 8D D4 4A A3 | 0.4...J.
1208 | D7 88 00 72 BA 13 0C 4D | .. r...M
1210 | 97 46 E0 BB 07 A6 EF FA | .F......
1218 | 12 0A FE 56 E9 14 2B DA | ...V..+.
1220 | 64 3C FE C5 3C A3 50 02 | d<..<.P.
1228 | 20 B7 20 05 3D DB F1 8A | ....=...
1230 | 81 41 4C 24 52 38 8F B9 | .AL$R8..
1238 | 7E 2E 6F 76 1C 3F 97 87 | ~.ov.?..
1240 | 16 D5 D3 C9 70 92 D7 D2 | ....p...
1248 | 47 59 E6 87 12 2C E0 A5 | GY...,..
1250 | 6C 17 9C BE EE E4 D4 50 | l......P
1258 | EA 94 57 91 4F B1 57 AA | ..W.O.W.
1260 | 46 E9 86 76 D3 F8 B9 A5 | F..v....
1268 | 8C 9C 57 56 0A 72 48 C8 | ..WV.rH.
1270 | 14 B6 8B F2 48 3C 4D B5 | ....H<M.
1278 | 3A 48 07 A6 F2 8E A3 0B | :H......
1280 | 39 02 75 9B C8 DC 6F 0A | 9.u...o.
1288 | 75 00 52 6D BF 77 89 2F | u Rm.w./
1290 | CE B0 27 EF 42 1E 36 E1 | ..'.B.6.
1298 | 37 C6 F7 77 34 1D 6A D3 | 7..w4.j.
12A0 | A7 48 6A C1 7D E7 76 8C | .Hj.}.v.
12A8 | 62 8F 62 8C 5C E4 F1 F3 | b.b.\...
12B0 | FD 5F B6 9D B4 D7 A8 A0 | ._......
12B8 | CD DE 8B 72 73 E4 FA E7 | ...rs...
12C0 | 33 8F 11 1E AF D3 40 A7 | 3.....@.
12C8 | 86 26 F3 77 4C 6E 2D 2D | .&.wLn--
12D0 | A4 03 C2 74 2E B3 DD 85 | ...t....
12D8 | 29 41 90 C3 C7 3A 96 B9 | )A...:..
12E0 | 8E 35 CF 37 C0 C8 FF D5 | .5.7....
12E8 | 8B 9F A1 D9 0F 8E 8E C6 | ........
12F0 | 11 C1 C0 C9 9E 5B 9C A1 | .....[..
12F8 | 2D C6 4B F5 34 65 B4 CC | -.K.4e..
1300 | AC 88 BF 49 43 77 AC 8F | ...ICw..
1308 | 61 71 8E 59 7F 78 D9 73 | aq.Y.x.s
1310 | 41 90 73 8B 8E 93 3F 6E | A.s...?n
1318 | DD 2E 37 E8 72 43 A1 F3 | ..7.rC..
1320 | A9 FE 7F 98 F3 A5 98 43 | .......C
1328 | E5 60 B9 5D BD BA 3F AE | .`.]..?.
1330 | 71 F6 ED C1 FE 8F 2D 15 | q.....-.
1338 | D9 C6 F7 57 83 57 7E 10 | ...W.W~.
1340 | B6 C3 76 29 B1 10 12 1E | ..v)....
1348 | EA A1 15 81 9C 22 5F 8A | ....."_.
1350 | F3 FF 1C 37 4E 57 1B 26 | ...7NW.&
1358 | 64 B7 CA 7C C8 57 D9 57 | d..|.W.W
"""

encrypted_data = []

for line in encrypted_data_dump.splitlines()[1:]:
    _addr, mem, _txt = line.split(" | ", 2)
    for b in mem.split():
        encrypted_data.append(int(b, 16))

assert len(encrypted_data) == 0x200, len(encrypted_data)

X = 0


def next_X():
    """
    Next_X:
2086 | B4 56 21 | ld R0 [.mem_X]               ; ($2156)
2089 | 01 A7 41 | mul R0 $41A7
208C | CF 55 55 | xor R0 $5555
208F | BC 56 21 | ld [.mem_X] R0               ; ($2156)
2092 | 05       | ret
    """
    global X
    X *= 0x41A7
    X &= 0xFFFF
    X ^= 0x5555
    return X


def decrypt(initial_X):
    """
204E | BC 56 21 | ld [.mem_X] R0               ; ($2156)
2051 | 13 60 21 | ld R3 .mem_encrypted         ; ($2160)
2054 | 12 60 23 | ld R2 .mem_output            ; ($2360)
2057 | 11 00 02 | ld R1 $0200
205A | 99 28 00 | call MemCpy                  ; ($0028)
205D | 12 60 23 | ld R2 .mem_output            ; ($2360)
2060 | 13 00 01 | ld R3 $0100
    .loop2:
2063 | 99 86 20 | call Next_X                  ; ($2086)
2066 | 24       | ld R1 R0
2067 | 52       | ld R0 [R2]
2068 | D9       | xor R0 R1
2069 | 78       | ld [R2] R0
206A | AA       | inc R2
206B | AA       | inc R2
206C | AF       | dec R3
206D | A5 00 00 | cmp R3 $0000
2070 | 9D 63 20 | jp ne .loop2  """
    global X
    X = initial_X

    output = []

    for i in range(0x100):
        X = next_X()
        data = encrypted_data[i*2] + 0x100*encrypted_data[i*2+1]
        data ^= X
        output.append(data & 0xFF)
        output.append(data >> 8)

    return bytes(output)


# print(decrypt(0x1337))

for x in range(0x10000):
    data = decrypt(x)
    if b"FOOLS2023_" in data:
        print(hex(x), data)
