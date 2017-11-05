from myhdl import *



@block
def Controller(op, funct, jump, branch, aluop, alusrc, regdst, regwrite, memwrite, memtoreg, sextend):

    """ MIPS controller unit

    op -- in
    funct -- in
    jump -- out bit
    branch -- out bit
    aluop -- out
    alusrc -- out bit
    regdst -- out bit
    regwrite -- out bit
    memwrite -- out bit
    memtoreg -- out bit
    sextend -- out bit
    """

    controls = Signal(modbv(0)[8:])

    @always_comb
    def logic2():
        jump.next = controls[7]
        branch.next = controls[6]
        alusrc.next = controls[5]
        regdst.next = controls[4]
        regwrite.next = controls[3]
        memwrite.next = controls[2]
        memtoreg.next = controls[1]
        sextend.next = controls[0]

    @always_comb
    def logic():
        if op == 0b000000: # R-type instructions

            controls.next = 0b00011000

            if   funct == 0b100000: aluop.next = 0b0110 # ADD
            elif funct == 0b100010: aluop.next = 0b1110 # SUB
            elif funct == 0b100100: aluop.next = 0b0000 # AND
            elif funct == 0b100101: aluop.next = 0b0001 # OR
            elif funct == 0b100110: aluop.next = 0b0010 # XOR
            elif funct == 0b100111: aluop.next = 0b0011 # NOR
            elif funct == 0b101010: aluop.next = 0b1111 # SLT
            else:
                aluop.next = 0
                #raise ValueError("Invalid ALU funct (%s)" % bin(funct))

        elif op == 0b000010:
            controls.next = 0b10000000
            aluop.next = 0b0000 # JUMP does not use alu
        elif op == 0b000100:
            controls.next = 0b01000000
            aluop.next = 0b1110 # SUB for BEQ
        elif op == 0b001000:
            controls.next = 0b00101001
            aluop.next = 0b0110 # ADD for ADDI
        elif op == 0b001010:
            controls.next = 0b00101001
            aluop.next = 0b1111 # SLT for SLTI
        elif op == 0b001100:
            controls.next = 0b00101000
            aluop.next = 0b0000 # AND for ANDI
        elif op == 0b001101:
            controls.next = 0b00101000
            aluop.next = 0b0001 # OR for ORI
        elif op == 0b001110:
            controls.next = 0b00101000
            aluop.next = 0b0010 # XOR for XORI
        elif op == 0b100011:
            controls.next = 0b00101011
            aluop.next = 0b0110 # ADD for LW
        elif op == 0b101011:
            controls.next = 0b00100101
            aluop.next = 0b0110 # ADD for SW
        else:
            controls.next = 0b00000000
            aluop.next = 0
            #raise ValueError("Invalid opcode")

    return instances()

if __name__ == '__main__':
    op = Signal(modbv(0)[6:])
    funct = Signal(modbv(0)[6:])
    jump = Signal(bool())
    branch = Signal(bool())
    aluop = Signal(modbv(0)[4:])
    alusrc = Signal(bool())
    regdst = Signal(bool())
    regwrite = Signal(bool())
    memwrite = Signal(bool())
    memtoreg = Signal(bool())
    sextend = Signal(bool())

    controller_inst = Controller(op, funct, jump, branch, aluop, alusrc, regdst, regwrite, memwrite, memtoreg, sextend)
    controller_inst.convert(hdl='VHDL')
