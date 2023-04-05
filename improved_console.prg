.inp_buffer=$E000

    ld sp $FF00
    ld R0 $FFF0
    ld R1 $98
    ldb [R0] R1
    inc R0
    ld R1 Breakpoint             ; ($F021)
    ld [R0] R1
    ld R2 .str_10_F33F_nWelcome  ; ($F33F)
    call PrintStr                ; ($08)
    BRK
    ld R2 .str_11_F7F3_Dry       ; ($F7F3)
    call PrintStr                ; ($08)
    int $03                      ; (halt)
.infloop_F01E:
    jp .infloop_F01E             ; ($F01E)

Breakpoint:
    push sp
    ld [.mem_R0] R0              ; ($FB3E)
    ld [.mem_R1] R1              ; ($FB40)
    ld [.mem_R2] R2              ; ($FB42)
    ld [.mem_R3] R3              ; ($FB44)
    pop R0
    ld [.mem_sp] R0              ; ($FB46)

    ld R0 .mem_after_flag-3
    ld R1 $3C           ; 3C = '<', 3D = '=', 3E = '>', 3F = '?' 
    jp gt .flag_gt 
    jp lt .flag_lt 
    jp eq .flag_eq
.flag_unk:
    inc R1
.flag_gt:
    inc R1 
.flag_eq:
    inc R1 
.flag_lt:
    ldb [R0] R1

    ld R0 sp
    ld R0 [R0]
    add R0 $FFFF
    ld [.mem_pc] R0           

    ld R1 $0C
    ld R2 .mem_at_sp
    ld R3 [.mem_sp]              
    call MemCpy                 

    ld R1 $0A
    ld R2 .mem_at_r0
    ld R3 [.mem_r0]              
    call MemCpy                  

    ld R1 $0A
    ld R2 .mem_at_r1
    ld R3 [.mem_r1]              
    call MemCpy                

    ld R1 $0A
    ld R2 .mem_at_r2
    ld R3 [.mem_r2]              
    call MemCpy                 

    ld R1 $0A
    ld R2 .mem_at_r3
    ld R3 [.mem_r3]              
    call MemCpy               

    ld R2 .str_break_into_monitor ; ($FAA4)
    call PrintStr                ; ($08)

InteractLoop:
    ld R0 $00
    ldb [.inp_buffer+2] R0       ; ($E002)
    ld R2 .str_13_FA9A_Ready     ; ($FA9A)
    call PrintStr                ; ($08)
    ld R2 .inp_buffer            ; ($E000)
    ld R3 $08
    call ReadStr                 ; ($30)
    cmp R3 $00
    jp eq .toolong               ; ($F0DC)
    ld R2 .inp_buffer            ; ($E000)
    call StrTrim                 ; ($38)
    ldb R0 [.inp_buffer+2]       ; ($E002)
    cmp R0 $00
    jp ne .badinp                ; ($F0D3)
    ld R0 [.inp_buffer]          ; ($E000)
    cmp R0 $A68
    jp eq .cmd_help              ; ($F0E5)
    cmp R0 $68
    jp eq .cmd_help              ; ($F0E5)
    cmp R0 $72
    jp eq .cmd_read              ; ($F0EE)
    cmp R0 $A72
    jp eq .cmd_read              ; ($F0EE)
    cmp R0 $70
    jp eq .cmd_print             ; ($F1ED)
    cmp R0 $A70
    jp eq .cmd_print             ; ($F1ED)
    cmp R0 $78
    jp eq .cmd_exec              ; ($F209)
    cmp R0 $A78
    jp eq .cmd_exec              ; ($F209)
    cmp R0 $63
    jp eq .cmd_continue          ; ($F24F)
    cmp R0 $A63
    jp eq .cmd_continue          ; ($F24F)
    cmp R0 $4355
    jp eq .cmd_undoc             ; ($F2A3)
    cmp R0 $736C
    jp eq .cmd_ls                ; ($F262)
    cmp R0 $6672
    jp eq .cmd_read_file         ; ($F2AC)
    cmp R0 $77
    jp eq .cmd_write             ; ($F15E)
    cmp R0 $A77
    jp eq .cmd_write             ; ($F15E)
.badinp:
    ld R2 .str_Bad_cmd           ; ($F73D)
    call PrintStr                ; ($08)
    jp InteractLoop              ; ($F04C)
.toolong:
    ld R2 .str_Inp_too_long      ; ($F724)
    call PrintStr                ; ($08)
    jp InteractLoop              ; ($F04C)
.cmd_help:
    ld R2 .str_16_F8AC_Available ; ($F8AC)
    call PrintStr                ; ($08)
    jp InteractLoop              ; ($F04C)
.cmd_read:
    ld R2 .str_Which_Addr        ; ($F778)
    call PrintStr                ; ($08)
    ld R2 .inp_buffer            ; ($E000)
    ld R3 $08
    call ReadStr                 ; ($30)
    ld R2 .inp_buffer            ; ($E000)
    call ConvertHex              ; ($20)
    cmp R0 $FFFF
    jp eq .read_invalid_inp      ; ($F155)
    push R0
    ld R2 .str_How_many_lines    ; ($F78A)
    call PrintStr                ; ($08)
    ld R2 .inp_buffer            ; ($E000)
    ld R3 $08
    call ReadStr                 ; ($30)
    ld R2 .inp_buffer            ; ($E000)
    call ConvertHex              ; ($20)
    cmp R0 $FFFF
    jp eq .read_invalid_inp      ; ($F155)
    cmp R0 $00
    jp eq .read_invalid_inp      ; ($F155)
    ld R3 R0
    pop R2
.read_mem_loop:
    push R2
    push R3
    ld R1 $08
    ld R3 R2
    ld R2 $FB56
    call MemCpy                  ; ($28)
    pop R3
    pop R2
    ld [$FB5E] R2
    push R2
    push R3
    ld R2 .str_mem_dump          ; ($FB17)
    call PrintStr                ; ($08)
    pop R3
    pop R2
    add R2 $08
    dec R3
    cmp R3 $00
    jp ne .read_mem_loop         ; ($F12D)
    jp InteractLoop              ; ($F04C)
.read_invalid_inp:
    ld R2 .str_Invalid_inp       ; ($F760)
    call PrintStr                ; ($08)
    jp InteractLoop              ; ($F04C)
.cmd_write:
    ld R2 .str_Which_Addr        ; ($F778)
    call PrintStr                ; ($08)
    ld R2 .inp_buffer            ; ($E000)
    ld R3 $08
    call ReadStr                 ; ($30)
    ld R2 .inp_buffer            ; ($E000)
    call ConvertHex              ; ($20)
    cmp R0 $FFFF
    jp eq .write_invalid_inp     ; ($F1E4)
    ld [$FB5E] R0
    ld R2 .str_enter_input       ; ($F838)
    call PrintStr                ; ($08)
.write_loop_outer:
    ld R3 .inp_buffer+2          ; ($E002)
    ld R0 $00
    ldb [R3] R0
    dec R3
    ldb [R3] R0
    dec R3
.write_loop_ch1:
    int $02                      ; (in)
    ldb [R3] R0
    ld R2 R3
    cmp R0 $2E
    jp eq .write_found_dot       ; ($F1D3)
    cmp R0 $0A
    jp eq .write_loop_ch1        ; ($F18C)
    push R3
    call ConvertHex              ; ($20)
    pop R3
    cmp R0 $FFFF
    jp eq .write_loop_ch1        ; ($F18C)
    inc R3
.write_loop_ch2:
    int $02                      ; (in)
    ldb [R3] R0
    ld R2 R3
    cmp R0 $2E
    jp eq .write_found_dot       ; ($F1D3)
    cmp R0 $0A
    jp eq .write_loop_ch2        ; ($F1A8)
    push R3
    call ConvertHex              ; ($20)
    pop R3
    cmp R0 $FFFF
    jp eq .write_loop_ch2        ; ($F1A8)
    dec R3
    ld R2 R3
    call ConvertHex              ; ($20)
    ld R1 [$FB5E]
    ldb [R1] R0
    inc R1
    ld [$FB5E] R1
    jp .write_loop_outer         ; ($F182)
.write_found_dot:
    int $02                      ; (in)
    cmp R0 $0A
    jp ne .write_found_dot       ; ($F1D3)
    ld R2 .str_23_F7EA_Loaded    ; ($F7EA)
    call PrintStr                ; ($08)
    jp InteractLoop              ; ($F04C)
.write_invalid_inp:
    ld R2 .str_Invalid_inp       ; ($F760)
    call PrintStr                ; ($08)
    jp InteractLoop              ; ($F04C)
.cmd_print:
    ld R2 .str_Which_Addr        ; ($F778)
    call PrintStr                ; ($08)
    ld R2 .inp_buffer            ; ($E000)
    ld R3 $08
    call ReadStr                 ; ($30)
    ld R2 .inp_buffer            ; ($E000)
    call ConvertHex              ; ($20)
    ld R2 R0
    call PrintStr                ; ($08)
    jp InteractLoop              ; ($F04C)
.cmd_exec:
    ld R2 .str_Which_Addr        ; ($F778)
    call PrintStr                ; ($08)
    ld R2 .inp_buffer            ; ($E000)
    ld R3 $08
    call ReadStr                 ; ($30)
    ld R2 .inp_buffer            ; ($E000)
    call ConvertHex              ; ($20)
    push R0
    ld [$FB5E] R0
    ld R2 .str_27_F79D_Really    ; ($F79D)
    call PrintStr                ; ($08)
    ld R2 .inp_buffer            ; ($E000)
    ld R3 $08
    call ReadStr                 ; ($30)
    ldb R0 [.inp_buffer]         ; ($E000)
    cmp R0 $59
    jp eq .exec_go               ; ($F24A)
    cmp R0 $79
    jp eq .exec_go               ; ($F24A)
    ld R2 .str_28_F7C2_Cancelled ; ($F7C2)
    call PrintStr                ; ($08)
    pop R0
    jp InteractLoop              ; ($F04C)
.exec_go:
    pop R3
    call R3
    jp InteractLoop              ; ($F04C)
.cmd_continue:
    ld R2 .str_29_F7DD_Continuing ; ($F7DD)
    call PrintStr                ; ($08)
    ld R0 [.mem_R0]              ; ($FB3E)
    ld R1 [.mem_R1]              ; ($FB40)
    ld R2 [.mem_R2]              ; ($FB42)
    ld R3 [.mem_R3]              ; ($FB44)
    ret
.cmd_ls:
    ld R2 .str_30_FA65_BLK       ; ($FA65)
    call PrintStr                ; ($08)
    ld R0 $00
    ld R1 .inp_buffer            ; ($E000)
    int $04                      ; (load_blk)
    ld R3 .inp_buffer            ; ($E000)
.ls_loop:
    ldb R0 [R3]
    cmp R0 $00
    jp eq .ls_next               ; ($F297)
    push R3
    ldb [$FB56] R0
    inc R3
    ld R0 [R3]
    push R3
    ld [$FB5E] R0
    ld R2 .str_ls_blk_size       ; ($FA8E)
    call PrintStr                ; ($08)
    pop R3
    inc R3
    inc R3
    ld R2 R3
    call PrintStr                ; ($08)
    ld R0 $0A
    int $01                      ; (out)
    pop R3
.ls_next:
    add R3 $10
    cmp R3 $EF00
    jp ne .ls_loop               ; ($F273)
    jp InteractLoop              ; ($F04C)
.cmd_undoc:
    ld R2 .str_32_F867_Wow       ; ($F867)
    call PrintStr                ; ($08)
    jp InteractLoop              ; ($F04C)
.cmd_read_file:
    ld R2 .str_Filename          ; ($F812)
    call PrintStr                ; ($08)
    ld R0 $00
    ld R1 .inp_buffer            ; ($E000)
    int $04                      ; (load_blk)
    ld R2 $EFB0
    ld R3 $10
    call ReadStr                 ; ($30)
    cmp R3 $00
    jp eq .readfile_toolong      ; ($F32D)
    ld R2 $EFB0
    call StrTrim                 ; ($38)
    ld R3 $E003
.readfile_search_loop:
    ld R2 $EFB0
    push R3
    call StrCmp                  ; ($10)
    pop R3
    cmp R0 $00
    jp eq .readfile_write        ; ($F2EC)
    add R3 $10
    cmp R3 $EF03
    jp eq .readfile_notfound     ; ($F324)
    jp .readfile_search_loop     ; ($F2D2)
.readfile_write:
    dec R3
    dec R3
    dec R3
    ldb R0 [R3]
    inc R3
    ld R1 [R3]
    push R1
    ld R1 .inp_buffer            ; ($E000)
    int $04                      ; (load_blk)
    ld R2 .str_Which_Addr        ; ($F778)
    call PrintStr                ; ($08)
    ld R2 $EFE0
    ld R3 $10
    call ReadStr                 ; ($30)
    ld R2 $EFE0
    call ConvertHex              ; ($20)
    pop R1
    cmp R0 $FFFF
    jp eq .readfile_invalid      ; ($F336)
    ld R2 R0
    ld R3 .inp_buffer            ; ($E000)
    call MemCpy                  ; ($28)
    ld R2 .str_23_F7EA_Loaded    ; ($F7EA)
    call PrintStr                ; ($08)
    jp InteractLoop              ; ($F04C)
.readfile_notfound:
    ld R2 .str_36_F81F_File      ; ($F81F)
    call PrintStr                ; ($08)
    jp InteractLoop              ; ($F04C)
.readfile_toolong:
    ld R2 .str_Inp_too_long      ; ($F724)
    call PrintStr                ; ($08)
    jp InteractLoop              ; ($F04C)
.readfile_invalid:
    ld R2 .str_Invalid_inp       ; ($F760)
    call PrintStr                ; ($08)
    jp InteractLoop              ; ($F04C)
.str_10_F33F_nWelcome:
ds "== Welcome ==\n\n"
.str_Inp_too_long:
    ds "! Input too long error.\n"
.str_Bad_cmd:
    ds "! Bad command error (h for help).\n"
.str_Invalid_inp:
    ds "! Invalid input error.\n"
.str_Which_Addr:
    ds "> Which address? "
.str_How_many_lines:
    ds "> How many lines? "
.str_27_F79D_Really:
ds "> Really exec at \F0[$FB5E]? Type Y if so: "
.str_28_F7C2_Cancelled:
    ds "! Cancelled action error.\n"
.str_29_F7DD_Continuing:
    ds "Continuing.\n"
.str_23_F7EA_Loaded:
    ds "Loaded.\n"
.str_11_F7F3_Dry:
    ds "! Dry stack. Halting machine.\n"
.str_Filename:
    ds "> Filename? "
.str_36_F81F_File:
    ds "! File not found error.\n"
.str_enter_input:
ds "> Enter hex data. End with dot \".\" + newline:\n"
.str_32_F867_Wow:
    ds "Wow, undocumented monitor command! FOOLS2023_{Secret\F0[.inp_buffer]x\F0[$E001]Command}\n" ; ($E000)
.str_16_F8AC_Available:
ds "Available commands:\nr   :: print memory as hex\np   :: print memory as text\nw   :: write hex data to memory\nx   :: execute memory\nrf  :: load memory from file\nls  :: print file index\nh   :: print this help message\nc   :: exit monitor and continue\nPlease enter hex numbers when prompted.\nIf necessary for debugging, you can break into monitor\nwith instruction BRK (0x00) and continue with 'c'\nNote: memory region E000-FFFF is used by monitor\n"
.str_30_FA65_BLK:
    ds "BLK  SIZE  NAME\n=======================\n"
.str_ls_blk_size:
    ds "\F1[$FB56]   \F0[$FB5E]  "
.str_13_FA9A_Ready:
    ds "Ready.\n> "
.str_break_into_monitor:
    ds """*** BREAK INTO MONITOR AT $\F0[.mem_pc] ***
R0=$\F0[.mem_R0] [\F0[.mem_at_r0] \F0[.mem_at_r0+2] \F0[.mem_at_r0+4] \F0[.mem_at_r0+6] \F0[.mem_at_r0+8]]
R1=$\F0[.mem_R1] [\F0[.mem_at_r1] \F0[.mem_at_r1+2] \F0[.mem_at_r1+4] \F0[.mem_at_r1+6] \F0[.mem_at_r1+8]]
R2=$\F0[.mem_R2] [\F0[.mem_at_r2] \F0[.mem_at_r2+2] \F0[.mem_at_r2+4] \F0[.mem_at_r2+6] \F0[.mem_at_r2+8]]
R3=$\F0[.mem_R3] [\F0[.mem_at_r3] \F0[.mem_at_r3+2] \F0[.mem_at_r3+4] \F0[.mem_at_r3+6] \F0[.mem_at_r3+8]]
SP=$\F0[.mem_sp] [\F0[.mem_at_sp] \F0[.mem_at_sp+2] \F0[.mem_at_sp+4] \F0[.mem_at_sp+6] \F0[.mem_at_sp+8] \F0[.mem_at_sp+10]]
FLAG=?
"""
.mem_after_flag:
    db $00
.str_mem_dump:
    ds "\F0[$FB5E] | \F1[$FB56] \F1[$FB57] \F1[$FB58] \F1[$FB59] \F1[$FB5A] \F1[$FB5B] \F1[$FB5C] \F1[$FB5D]\n"
.mem_R0:
    dw $0000
.mem_R1:
    dw $0000
.mem_R2:
    dw $0000
.mem_R3:
    dw $0000
.mem_sp:
   dw $0000
.mem_pc:
    dw $0000
.mem_at_sp:
    dw $0000
    dw $0000
    dw $0000
    dw $0000
    dw $0000
    dw $0000
.mem_at_r0:
    dw $0000
    dw $0000
    dw $0000
    dw $0000
    dw $0000
.mem_at_r1:
    dw $0000
    dw $0000
    dw $0000
    dw $0000
    dw $0000
.mem_at_r2:
    dw $0000
    dw $0000
    dw $0000
    dw $0000
    dw $0000
.mem_at_r3:
    dw $0000
    dw $0000
    dw $0000
    dw $0000
    dw $0000

