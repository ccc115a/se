int16_t D = 0, A = 0, PC = 0, IR = 0;

#define ALU(IR) (c = (I & 0x0FC0) >>  6; aluOut = 
#define FETCH IR = im[PC]
#define IA    A = IR
#define IC    ALU()


  a = (I & 0x1000) >> 12;
  
  d = (I & 0x0038) >>  3;
  j = (I & 0x0007) >>  0;
