from math import log2

DSIZE = 32 # data size
ASIZE = 32 # address size
RAM_DEPTH = 128 # RAM size in words
NUM_REGS = 32 # number of registers
REG_ASIZE = int(log2(NUM_REGS)) # register address size

ALU_FUN_SIZE = 4

OPCODE_SIZE = 6
OPCODE_RANGE = (32, 26)
FUNCT_SIZE = 6
FUNCT_RANGE = (6, 0)
IMMEDIATE_SIZE = 16
IMMEDIATE_RANGE = (16, 0)

RS_RANGE = (26, 21)
RT_RANGE = (21, 16)
RD_RANGE = (16, 11)

JUMP_IMM_RANGE = (26, 0)
