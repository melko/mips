from myhdl import *
from math import log2

@block
def Dmem(clk, we, addr, wd, rd, depth=64):

    """ A simple memory

    clk -- in
    we -- in - write enable
    addr -- in vec - read/write address
    wd -- in vec - data to be written
    rd -- out vec - data to be read

    """

    addr_width = int(log2(depth))
    iaddr = addr(addr_width + 2, 2)

    RAM = [Signal(modbv(wd.val)) for i in range(depth)]

    @always(clk.posedge)
    def write_logic():
        if we:
            #RAM[int(addr >> 2)].next = wd
            RAM[int(iaddr)].next = wd

    @always_comb
    def read_logic():
        rd.next = RAM[int(iaddr)]

    return instances()


if __name__ == '__main__':
    clk = Signal(bool())
    we = Signal(bool())
    addr = Signal(modbv(0)[32:])
    wd = Signal(modbv(0)[32:])
    rd = Signal(modbv(0)[32:])

    dmem_inst = Dmem(clk, we, addr, wd, rd)
    dmem_inst.convert(hdl='VHDL')
