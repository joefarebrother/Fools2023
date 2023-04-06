MemBreakpoint=$FFF0 

Start:
  ld R3 MemBreakpoint 
  ld R2 NormalBreakpoint
  ld R1 $03 
  call MemCpy 

  ld R3 NewBreakpoint 
  ld R2 MemBreakpoint
  ld R1 $04 
  call MemCpy 

  ;ld R2 .str_hello_pre
  ;call PrintStr 

  ; call NormalBreakpoint
  ;brk

  db $07
  db $FF

  ret

NormalBreakpoint:
  db 0
  db 0
  db 0

NewBreakpoint:
  db $F8
  jp NewBreakpointPtr

NewBreakpointPtr:
  ld R3 NormalBreakpoint 
  ld R2 MemBreakpoint 
  ld R1 $03
  call MemCpy 

  ld R0 sp 
  ld R3 .mem_sp 
  ld [R3] R0
  inc R3 
  inc R3 
  ld R0 [R0]
  ld [R3] R0

  ld R2 .str_hello
  call PrintStr 

  jp MemBreakpoint

.str_hello:
  ds "Goodbye! \F1[$FFF0] \F1[$FFF1] \F1[$FFF2] \F1[$FFF3] \F0[.mem_sp] \F0[.mem_sp+2]\n"

.str_hello_pre:
  ds "Hello! \F1[$FFF0] \F1[$FFF1] \F1[$FFF2] \F1[$FFF3] \n"

.mem_sp: