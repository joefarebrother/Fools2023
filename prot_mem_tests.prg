Start:
  ld R3 $6969
  ld [R3] R3 
  ld R2 $01CD 
  call MemCpy1 ; write $69 to $0420
  ld R3 $01CD
  ld R2 $1337 
  call MemCpy1 ; read from $0420 to $1337
  ld R1 [$1337] 
  brk


MemCpy1:       ; R2 = dest, R3 = src 
  ld R1 $0001
  jp $01E8