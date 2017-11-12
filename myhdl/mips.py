from myhdl import *
from datapath import Datapath
from controller import Controller
import config

@block
def Mips(clk, reset, pc, instr, memwrite, aluout, writedata, readdata):

    """ Mips top level

    clk -- in
    reset -- in
    pc -- out vec
    instr -- in vec
    memwrite -- out
    aluout -- out vec
    writedata -- out vec
    readdata -- in vec

    """

    op = instr(*config.OPCODE_RANGE)
    funct = instr(*config.FUNCT_RANGE)

    memtoreg = Signal(bool())
    alusrc = Signal(bool())
    regdst = Signal(bool())
    regwrite = Signal(bool())
    jump = Signal(bool())
    branch = Signal(bool())
    sextend = Signal(bool())

    aluop = Signal(modbv(0)[config.ALU_FUN_SIZE:])

    controller_inst = Controller(op, funct, jump, branch, aluop, alusrc, regdst, regwrite, memwrite, memtoreg, sextend)

    datapath_inst = Datapath(clk, reset, instr, pc, readdata, writedata, aluout, jump, branch, aluop, alusrc, regdst, regwrite, memtoreg, sextend)

    return instances()


if __name__ == '__main__':
    clk = Signal(bool())
    reset = ResetSignal(0, active=1, async=True)
    pc = Signal(modbv(0)[config.ASIZE:])
    instr = Signal(modbv(0)[config.DSIZE:])
    memwrite = Signal(bool())
    aluout = Signal(modbv(0)[config.DSIZE:])
    writedata = Signal(modbv(0)[config.DSIZE:])
    readdata = Signal(modbv(0)[config.DSIZE:])

    mips_inst = Mips(clk, reset, pc, instr, memwrite, aluout, writedata, readdata)
    mips_inst.convert(hdl='verilog')
