.normal_Breakpoint=$F021
.normal_InteractLoop=$F04C

    ld sp $FF00
    ld R0 $FFF0
    ld R1 $98
    ldb [R0] R1
    inc R0
    ld R2 [R0]
    add R2 (.normal_InteractLoop-.normal_Breakpoint)
    ld R3 .mem_InteractLoopPtr 
    ld [R3] R2
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

MemCpy1:       ; R2 = dest, R3 = src 
  ld R1 $0001
  jp $01E8

GoodMemCpy:
  push R1 
  call MemCpy1 
  pop R1 
  dec R1 
  cmp R1 $0000 
  jp ne GoodMemCpy
  ret

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

    ld R1 $08
    ld R2 .mem_at_r0
    ld R3 [.mem_r0]     
    dec R3
    dec R3       
    call GoodMemCpy                  

    ld R1 $08
    ld R2 .mem_at_r1
    ld R3 [.mem_r1]    
    dec R3
    dec R3          
    call GoodMemCpy                

    ld R1 $08
    ld R2 .mem_at_r2
    ld R3 [.mem_r2]    
    dec R3
    dec R3        
    call GoodMemCpy                 

    ld R1 $08
    ld R2 .mem_at_r3
    ld R3 [.mem_r3]    
    dec R3
    dec R3        
    call GoodMemCpy               

    ld R2 .str_break_into_monitor ; ($FAA4)
    call PrintStr                ; ($08)

    db $98 ; jp $XXXX
.mem_InteractLoopPtr:
  dw $0000



.str_10_F33F_nWelcome:
ds "== Welcome ==\n\n"

.str_11_F7F3_Dry:
    ds "! Dry stack. Halting machine.\n"

.str_break_into_monitor:
    ds """*** BREAK INTO MONITOR AT $\F0[.mem_pc] ***
R0=$\F0[.mem_R0] [\F1[.mem_at_r0] \F1[.mem_at_r0+1] [\F1[.mem_at_r0+2] \F1[.mem_at_r0+3]] \F1[.mem_at_r0+4] \F1[.mem_at_r0+5] \F1[.mem_at_r0+6] \F1[.mem_at_r0+7] \F1[.mem_at_r0+8]]
R1=$\F0[.mem_R1] [\F1[.mem_at_r1] \F1[.mem_at_r1+1] [\F1[.mem_at_r1+2] \F1[.mem_at_r1+3]] \F1[.mem_at_r1+4] \F1[.mem_at_r1+5] \F1[.mem_at_r1+6] \F1[.mem_at_r1+7] \F1[.mem_at_r1+8]]
R2=$\F0[.mem_R2] [\F1[.mem_at_r2] \F1[.mem_at_r2+1] [\F1[.mem_at_r2+2] \F1[.mem_at_r2+3]] \F1[.mem_at_r2+4] \F1[.mem_at_r2+5] \F1[.mem_at_r2+6] \F1[.mem_at_r2+7] \F1[.mem_at_r2+8]]
R3=$\F0[.mem_R3] [\F1[.mem_at_r3] \F1[.mem_at_r3+1] [\F1[.mem_at_r3+2] \F1[.mem_at_r3+3]] \F1[.mem_at_r3+4] \F1[.mem_at_r3+5] \F1[.mem_at_r3+6] \F1[.mem_at_r3+7] \F1[.mem_at_r3+8]]
SP=$\F0[.mem_sp] [\F0[.mem_at_sp] \F0[.mem_at_sp+2] \F0[.mem_at_sp+4] \F0[.mem_at_sp+6] \F0[.mem_at_sp+8] \F0[.mem_at_sp+10]]
FLAG:?
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

