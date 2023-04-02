nop                                                 ; 3009 | 20
push R1                                             ; 300A | 91
push R2                                             ; 300B | 92                                         
push R3                                             ; 300C | 93

ld R1 $0000           ; r1 = i                      ; 300D | 11 00 00             
.searchloop:                                        
ld R2 R1                                            ; 3010 | 26 
add R2 R2                                           ; 3011 | 3A
add R2 sqr_tab        ; [r2] = i^2                  ; 3012 | E2 32 30           
ld [dummylab+1] R2                                  ; 3015 | BE 19 30    
.dummylab:                                         
ld R3 [0000]          ; r3 = i^2                    ; 3018 | B7 00 00  
ld [dummylab2+1] R3                                 ; 301B | BF 1D 30
.dummylab2:                                       
cmp R0 $0000          ; X <=>  i^2                  ; 301C | A2 00 00                                                 
jp lt .exit           ; if X < i^2                  ; 3021 | 9A 2A 30                     
add R1 $0001                                        ; 3024 | E1 01 00 
jp .search_loop                                     ; 3027 | 98 10 30

.exit:       ; X < i^2                              
ld R0 R3                                            ; 302A | 2C 
add R0 $FFFF ; return i-1                           ; 302B | E0 FF FF

pop R3                                              ; 302E | 97
pop R2                                              ; 302F | 96
pop R1                                              ; 3030 | 95
ret                                                 ; 3031 | 05


.sqr_tab:                                           ; 3032
dw $0000
dw $0001
dw $0004
dw $0009
dw $0010
dw $0019
dw $0024
dw $0031
dw $0040
dw $0051
dw $0064
dw $0079
dw $0090
dw $00A9
dw $00C4
dw $00E1
dw $0100
dw $0121
dw $0144
dw $0169
dw $0190
dw $01B9
dw $01E4
dw $0211
dw $0240
dw $0271
dw $02A4
dw $02D9
dw $0310
dw $0349
dw $0384
dw $03C1
dw $0400
dw $0441
dw $0484
dw $04C9
dw $0510
dw $0559
dw $05A4
dw $05F1
dw $0640
dw $0691
dw $06E4
dw $0739
dw $0790
dw $07E9
dw $0844
dw $08A1
dw $0900
dw $0961
dw $09C4
dw $0A29
dw $0A90
dw $0AF9
dw $0B64
dw $0BD1
dw $0C40
dw $0CB1
dw $0D24
dw $0D99
dw $0E10
dw $0E89
dw $0F04
dw $0F81
dw $1000
dw $1081
dw $1104
dw $1189
dw $1210
dw $1299
dw $1324
dw $13B1
dw $1440
dw $14D1
dw $1564
dw $15F9
dw $1690
dw $1729
dw $17C4
dw $1861
dw $1900
dw $19A1
dw $1A44
dw $1AE9
dw $1B90
dw $1C39
dw $1CE4
dw $1D91
dw $1E40
dw $1EF1
dw $1FA4
dw $2059
dw $2110
dw $21C9
dw $2284
dw $2341
dw $2400
dw $24C1
dw $2584
dw $2649
dw $2710
dw $27D9
dw $28A4
dw $2971
dw $2A40
dw $2B11
dw $2BE4
dw $2CB9
dw $2D90
dw $2E69
dw $2F44
dw $3021
dw $3100
dw $31E1
dw $32C4
dw $33A9
dw $3490
dw $3579
dw $3664
dw $3751
dw $3840
dw $3931
dw $3A24
dw $3B19
dw $3C10
dw $3D09
dw $3E04
dw $3F01
dw $4000
dw $4101
dw $4204
dw $4309
dw $4410
dw $4519
dw $4624
dw $4731
dw $4840
dw $4951
dw $4A64
dw $4B79
dw $4C90
dw $4DA9
dw $4EC4
dw $4FE1
dw $5100
dw $5221
dw $5344
dw $5469
dw $5590
dw $56B9
dw $57E4
dw $5911
dw $5A40
dw $5B71
dw $5CA4
dw $5DD9
dw $5F10
dw $6049
dw $6184
dw $62C1
dw $6400
dw $6541
dw $6684
dw $67C9
dw $6910
dw $6A59
dw $6BA4
dw $6CF1
dw $6E40
dw $6F91
dw $70E4
dw $7239
dw $7390
dw $74E9
dw $7644
dw $77A1
dw $7900
dw $7A61
dw $7BC4
dw $7D29
dw $7E90
dw $7FF9
dw $8164
dw $82D1
dw $8440
dw $85B1
dw $8724
dw $8899
dw $8A10
dw $8B89
dw $8D04
dw $8E81
dw $9000
dw $9181
dw $9304
dw $9489
dw $9610
dw $9799
dw $9924
dw $9AB1
dw $9C40
dw $9DD1
dw $9F64
dw $A0F9
dw $A290
dw $A429
dw $A5C4
dw $A761
dw $A900
dw $AAA1
dw $AC44
dw $ADE9
dw $AF90
dw $B139
dw $B2E4
dw $B491
dw $B640
dw $B7F1
dw $B9A4
dw $BB59
dw $BD10
dw $BEC9
dw $C084
dw $C241
dw $C400
dw $C5C1
dw $C784
dw $C949
dw $CB10
dw $CCD9
dw $CEA4
dw $D071
dw $D240
dw $D411
dw $D5E4
dw $D7B9
dw $D990
dw $DB69
dw $DD44
dw $DF21
dw $E100
dw $E2E1
dw $E4C4
dw $E6A9
dw $E890
dw $EA79
dw $EC64
dw $EE51
dw $F040
dw $F231
dw $F424
dw $F619
dw $F810
dw $FA09
dw $FC04
dw $FE01