from myhdl import *
from alu import ALU
from regfile import Regfile

@block
def Datapath(clk, reset, instruction, pc, readdata, writedata, aluout, jump, branch, aluop, alusrc, regdst, regwrite, memtoreg, sextend):

    """ MIPS datapath

    clk -- in - no description needed
    reset -- in - same

    instruction -- in (vec) - comes from instruction memory
    pc -- out (vec) - program counter, goes to instruction memory
    readdata -- in (vec) - comes from data memory
    writedata -- out (vec) - goes to data memory
    aluout -- out (vec) - address for data memory

    jump -- in
    branch -- in
    aluop -- in (vec)
    alusrc -- in
    regdst -- in
    regwrite -- in
    memtoreg -- in
    sextend -- in

    """

    # program counter logic
    pc_next = Signal(pc.val)
    i_pc = Signal(pc.val)
    pcplus4 = Signal(pc.val)
    pcbranch = Signal(pc.val)
    pcbranchm = Signal(pc.val)
    pcjump = Signal(pc.val)

    branchgate = Signal(bool())
    signimm = Signal(instruction.val.signed())
    #signext = [instruction(15) for i in range(16)]
    #signimm = ConcatSignal(*signext, instruction(16, 0))
    signimmsh = Signal(instruction.val)
    immediate = Signal(instruction.val)
    unsignimm = instruction(16, 0)

    srca = Signal(instruction.val)
    srcb = Signal(instruction.val)
    aluzero = Signal(bool())
    i_aluout = Signal(aluout.val)
    alu_inst = ALU(srca, srcb, aluop, i_aluout, aluzero)

    ra1 = instruction(26, 21)
    ra2 = instruction(21, 16)
    rfwadd = Signal(modbv(0)[4:])
    rfwdata = Signal(instruction.val)
    rfrd2 = Signal(instruction.val)
    regfile_inst = Regfile(clk, ra1, ra2, rfwadd, rfwdata, regwrite, srca, rfrd2)

    @always_seq(clk.posedge, reset=reset)
    def pc_seq():
        i_pc.next = pc_next

    @always_comb
    def pc_comb():
        pc_next.next = pcjump if jump else pcbranchm
        pcbranch.next = signimmsh + pcplus4

        branchgate.next = aluzero & branch

        rfwadd.next = instruction[16:11] if regdst else instruction[21:16]
        rfwdata.next = readdata if memtoreg else i_aluout
        srcb.next = immediate if alusrc else rfrd2

        writedata.next = rfrd2
        pc.next = i_pc
        aluout.next = i_aluout

    @always_comb
    def logic():
        pcbranchm.next = pcbranch if branchgate else pcplus4
        immediate.next = signimm[len(signimm):] if sextend else unsignimm
        pcjump.next = concat(pcplus4[32:28], instruction[26:], modbv(0)[2:])
        signimmsh.next = (signimm << 2)[len(signimmsh):]

    @always_comb
    def logic2():
        signimm.next = instruction[16:].signed()
        pcplus4.next = i_pc + 4

    return instances()

if __name__ == '__main__':
    clk = Signal(bool())
    reset = ResetSignal(0, active=1, async=True)
    instruction = Signal(modbv(0)[32:])
    pc = Signal(instruction.val)
    readdata = Signal(instruction.val)
    writedata = Signal(instruction.val)
    aluout = Signal(instruction.val)
    jump = Signal(bool())
    branch = Signal(bool())
    aluop = Signal(modbv(0)[4:])
    alusrc = Signal(bool())
    regdst = Signal(bool())
    regwrite = Signal(bool())
    memtoreg = Signal(bool())
    sextend = Signal(bool())

    datapath_inst = Datapath(clk, reset, instruction, pc, readdata, writedata, aluout, jump, branch, aluop, alusrc, regdst, regwrite, memtoreg, sextend)
    datapath_inst.convert(hdl='VHDL')
