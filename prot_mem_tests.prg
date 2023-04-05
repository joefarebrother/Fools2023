ld R3 $0000
ld R2 $1000
.loop:
  call MemCpy1 
  cmp R3 $1000
  jp ne .loop
  ret


MemCpy1:       ; R2 = dest, R3 = src 
  ld R1 $0001
  jp $01E8