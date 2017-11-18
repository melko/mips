from myhdl import *
from regfile import Regfile
import config

MIPS_OPS = enum(
    'OP_ADD', 'OP_SUB', 'OP_AND', 'OP_OR', 'OP_XOR', 'OP_NOR', 'OP_SLT',
    'OP_BEQ', 'OP_ADDI', 'OP_SLTI', 'OP_ANDI', 'OP_ORI', 'OP_XORI', 'OP_LW', 'OP_SW',
    'OP_JUMP',
)

def isRtype(op):
    if op==MIPS_OPS.OP_ADD or op==MIPS_OPS.OP_SUB or op==MIPS_OPS.OP_AND or op==MIPS_OPS.OP_OR or op==MIPS_OPS.OP_XOR or op==MIPS_OPS.OP_NOR or op==MIPS_OPS.OP_SLT:
        return True
    else:
        return False

def isItype(op):
    if op==MIPS_OPS.OP_BEQ or op==MIPS_OPS.OP_ADDI or op==MIPS_OPS.OP_SLTI or op==MIPS_OPS.OP_ANDI or op==MIPS_OPS.OP_ORI or op==MIPS_OPS.OP_XORI or op==MIPS_OPS.OP_LW or op==MIPS_OPS.OP_SW:
        return True
    else:
        return False

@block
def Mips(clk, reset, pc, instr, memwrite, daddr, writedata, readdata):

    """ Mips top level

    clk -- in
    reset -- in
    pc -- out vec
    instr -- in vec
    memwrite -- out
    daddr -- out vec
    writedata -- out vec
    readdata -- in vec

    """

    op = instr(*config.OPCODE_RANGE)
    funct = instr(*config.FUNCT_RANGE)
    decoded_op = Signal(MIPS_OPS.OP_ADD)

    i_pc = Signal(modbv(0, _nrbits=config.ASIZE))
    pcplus4 = Signal(modbv(0, _nrbits=config.ASIZE))

    op_rs = instr(*config.RS_RANGE)
    op_rt = instr(*config.RT_RANGE)
    op_rd = instr(*config.RD_RANGE)
    op_immediate = instr(*config.IMMEDIATE_RANGE)
    op_target = instr(*config.JUMP_IMM_RANGE)

    rf_wa = Signal(intbv(0, _nrbits=config.REG_ASIZE))
    rf_wd = Signal(modbv(0, _nrbits=config.DSIZE))
    rf_we = Signal(bool(False))
    rf_rd1 = Signal(modbv(0, _nrbits=config.DSIZE))
    rf_rd2 = Signal(modbv(0, _nrbits=config.DSIZE))
    rf_inst = Regfile(clk, op_rs, op_rt, rf_wa, rf_wd, rf_we, rf_rd1, rf_rd2, DEPTH=config.NUM_REGS)

    @always_seq(clk.posedge, reset)
    def pc_logic():

        i_pc.next = pcplus4
        if decoded_op == MIPS_OPS.OP_BEQ:
            if rf_rd1 == rf_rd2:
                i_pc.next = pcplus4 + (op_immediate.signed() << 2)
        elif decoded_op == MIPS_OPS.OP_JUMP:
            i_pc.next = concat(pcplus4[:(len(op_target)+2)], op_target, intbv(0)[2:])

    @always_comb
    def comb_logic():
        pcplus4.next = i_pc + 4
        pc.next = i_pc

        memwrite.next = False
        daddr.next = 0
        writedata.next = 0

        rf_wa.next = 0
        rf_wd.next = 0
        rf_we.next = False

        if isRtype(decoded_op):
            rf_wa.next = op_rd
            rf_we.next = True

            if decoded_op == MIPS_OPS.OP_ADD:
                rf_wd.next = rf_rd1 + rf_rd2
            elif decoded_op == MIPS_OPS.OP_SUB:
                rf_wd.next = rf_rd1 - rf_rd2
            elif decoded_op == MIPS_OPS.OP_AND:
                rf_wd.next = rf_rd1 & rf_rd2
            elif decoded_op == MIPS_OPS.OP_OR:
                rf_wd.next = rf_rd1 | rf_rd2
            elif decoded_op == MIPS_OPS.OP_XOR:
                rf_wd.next = rf_rd1 ^ rf_rd2
            elif decoded_op == MIPS_OPS.OP_NOR:
                rf_wd.next = ~(rf_rd1 | rf_rd2)
            elif decoded_op == MIPS_OPS.OP_SLT:
                if rf_rd1.signed() < rf_rd2.signed():
                    rf_wd.next = 1
                else:
                    rf_wd.next = 0
        elif isItype(decoded_op):
            rf_wa.next = op_rt
            rf_we.next = True

            if decoded_op == MIPS_OPS.OP_BEQ:
                rf_we.next = False
            if decoded_op == MIPS_OPS.OP_ADDI:
                rf_wd.next = rf_rd1 + op_immediate.signed()
            if decoded_op == MIPS_OPS.OP_SLTI:
                if rf_rd1.signed() < op_immediate.signed():
                    rf_wd.next = 1
                else:
                    rf_wd.next = 0
            if decoded_op == MIPS_OPS.OP_ANDI:
                rf_wd.next = rf_rd1 & op_immediate
            if decoded_op == MIPS_OPS.OP_ORI:
                rf_wd.next = rf_rd1 | op_immediate
            if decoded_op == MIPS_OPS.OP_XORI:
                rf_wd.next = rf_rd1 ^ op_immediate
            if decoded_op == MIPS_OPS.OP_LW:
                daddr.next = rf_rd1 + op_immediate.signed()
                rf_wd.next = readdata
            if decoded_op == MIPS_OPS.OP_SW:
                daddr.next = rf_rd1 + op_immediate.signed()
                writedata.next = rf_rd2
                memwrite.next = True
                rf_we.next = False


    @always_comb
    def decode_opcode():
        if op == 0b000000: # R-type instructions

            if   funct == 0b100000: decoded_op.next = MIPS_OPS.OP_ADD
            elif funct == 0b100010: decoded_op.next = MIPS_OPS.OP_SUB
            elif funct == 0b100100: decoded_op.next = MIPS_OPS.OP_AND
            elif funct == 0b100101: decoded_op.next = MIPS_OPS.OP_OR
            elif funct == 0b100110: decoded_op.next = MIPS_OPS.OP_XOR
            elif funct == 0b100111: decoded_op.next = MIPS_OPS.OP_NOR
            elif funct == 0b101010: decoded_op.next = MIPS_OPS.OP_SLT
            else:
                decoded_op.next = MIPS_OPS.OP_ADD
                #raise ValueError("R-type instruction not implemented %s" % instr)

        elif op == 0b000010:
            decoded_op.next = MIPS_OPS.OP_JUMP
        elif op == 0b000100:
            decoded_op.next = MIPS_OPS.OP_BEQ
        elif op == 0b001000:
            decoded_op.next = MIPS_OPS.OP_ADDI
        elif op == 0b001010:
            decoded_op.next = MIPS_OPS.OP_SLTI
        elif op == 0b001100:
            decoded_op.next = MIPS_OPS.OP_ANDI
        elif op == 0b001101:
            decoded_op.next = MIPS_OPS.OP_ORI
        elif op == 0b001110:
            decoded_op.next = MIPS_OPS.OP_XORI
        elif op == 0b100011:
            decoded_op.next = MIPS_OPS.OP_LW
        elif op == 0b101011:
            decoded_op.next = MIPS_OPS.OP_SW
        else:
            decoded_op.next = MIPS_OPS.OP_ADD
            if not reset and clk==1:
                print("Instruction %s not implemented" % instr)
                #raise ValueError("Instruction not implemented")


    return instances()

if __name__ == '__main__':
    clk = Signal(bool())
    reset = ResetSignal(0, active=1, async=True)
    pc = Signal(modbv(0)[config.ASIZE:])
    instr = Signal(modbv(0)[config.DSIZE:])
    memwrite = Signal(bool())
    daddr = Signal(modbv(0)[config.DSIZE:])
    writedata = Signal(modbv(0)[config.DSIZE:])
    readdata = Signal(modbv(0)[config.DSIZE:])

    mips_inst = Mips(clk, reset, pc, instr, memwrite, daddr, writedata, readdata)
    mips_inst.convert(hdl='verilog')
