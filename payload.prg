  ld R0 $0045
  int $1 ; output a E so the client can see it
  
  ld R2 $F000
  ld R3 $0B60
Loop:
  int $2 ; read to R0 
  ldb [R2] R0 
  inc R2 
  dec R3 
  cmp R3 $0000 
  jp ne Loop

  jp $F000
