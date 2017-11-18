from myhdl import *
from alu import ALU
from regfile import Regfile
import config

@block
def Datapath(clk, reset, instruction, pc, readdata, writedata, aluout, jump, branch, aluop, alusrc, regdst, regwrite, memtoreg, sextend):

    """ MIPS datapath

    clk -- in - no description needed
    reset -- in - same

    instruction -- in vec - comes from instruction memory
    pc -- out vec - program counter, goes to instruction memory
    readdata -- in vec - comes from data memory
    writedata -- out vec - goes to data memory
    aluout -- out vec - address for data memory

    jump -- in
    branch -- in
    aluop -- in vec
    alusrc -- in
    regdst -- in
    regwrite -- in
    memtoreg -- in
    sextend -- in

    """

    # program counter logic
    pc_next = Signal(intbv(0, _nrbits=config.ASIZE))
    i_pc = Signal(intbv(0, _nrbits=config.ASIZE))
    pcplus4 = Signal(modbv(0, _nrbits=config.ASIZE))
    pcbranch = Signal(modbv(0, _nrbits=config.ASIZE))
    pcbranchm = Signal(intbv(0, _nrbits=config.ASIZE))
    pcjump = Signal(intbv(0, _nrbits=config.ASIZE))

    branchgate = Signal(bool())
    signimm = Signal(intbv(0, _nrbits=config.ASIZE).signed())
    signimmsh = Signal(modbv(0, _nrbits=config.ASIZE))
    immediate = Signal(intbv(0, _nrbits=config.ASIZE))

    unsignimm = instruction(*config.IMMEDIATE_RANGE)

    # alu
    srca = Signal(intbv(0, _nrbits=config.DSIZE))
    srcb = Signal(intbv(0, _nrbits=config.DSIZE))
    aluzero = Signal(bool())
    i_aluout = Signal(intbv(0, _nrbits=config.DSIZE))

    alu_inst = ALU(srca, srcb, aluop, i_aluout, aluzero)

    # register file
    rs_addr = instruction(*config.RS_RANGE)
    rt_addr = instruction(*config.RT_RANGE)
    rd_addr = instruction(*config.RD_RANGE)
    rfwadd = Signal(intbv(0, _nrbits=config.REG_ASIZE))
    rfwdata = Signal(intbv(0, _nrbits=config.ASIZE))
    rfrd2 = Signal(intbv(0, _nrbits=config.ASIZE))

    regfile_inst = Regfile(clk, rs_addr, rt_addr, rfwadd, rfwdata, regwrite, srca, rfrd2)

    jump_imm_op = instruction(*config.JUMP_IMM_RANGE)

    @always_seq(clk.posedge, reset=reset)
    def pc_seq():
        i_pc.next = pc_next

    @always_comb
    def pc_comb():
        pc_next.next = pcjump if jump else pcbranchm
        pcbranch.next = signimmsh + pcplus4

        branchgate.next = aluzero & branch

        rfwadd.next = rd_addr if regdst else rt_addr
        rfwdata.next = readdata if memtoreg else i_aluout
        srcb.next = immediate if alusrc else rfrd2

        writedata.next = rfrd2
        pc.next = i_pc
        aluout.next = i_aluout

    @always_comb
    def logic():
        pcbranchm.next = pcbranch if branchgate else pcplus4
        immediate.next = signimm[len(signimm):] if sextend else unsignimm
        pcjump.next = concat(pcplus4[:(len(jump_imm_op)+2)], jump_imm_op, intbv(0)[2:])
        signimmsh.next = (signimm << 2)

    @always_comb
    def logic2():
        signimm.next = unsignimm.signed()
        pcplus4.next = i_pc + 4

    return instances()

if __name__ == '__main__':
    clk = Signal(bool())
    reset = ResetSignal(0, active=1, async=True)
    instruction = Signal(intbv(0, _nrbits=config.DSIZE))
    pc = Signal(intbv(0, _nrbits=config.ASIZE))
    readdata = Signal(intbv(0, _nrbits=config.DSIZE))
    writedata = Signal(intbv(0, _nrbits=config.DSIZE))
    aluout = Signal(intbv(0, _nrbits=config.DSIZE))
    jump = Signal(bool())
    branch = Signal(bool())
    aluop = Signal(modbv(0, _nrbits=config.ALU_FUN_SIZE))
    alusrc = Signal(bool())
    regdst = Signal(bool())
    regwrite = Signal(bool())
    memtoreg = Signal(bool())
    sextend = Signal(bool())

    datapath_inst = Datapath(clk, reset, instruction, pc, readdata, writedata, aluout, jump, branch, aluop, alusrc, regdst, regwrite, memtoreg, sextend)
    datapath_inst.convert(hdl='VHDL')
