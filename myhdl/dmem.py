from myhdl import *
from math import log2
import config

@block
def Dmem(clk, we, addr, wd, rd, WORD_SIZE=32, DEPTH=64):

    """ A simple memory

    clk -- in
    we -- in - write enable
    addr -- in vec - read/write address
    wd -- in vec - data to be written
    rd -- out vec - data to be read

    """

    addr_width = int(log2(DEPTH))
    iaddr = addr(addr_width + 2, 2)

    RAM = [Signal(intbv(0, _nrbits=WORD_SIZE)) for i in range(DEPTH)]

    @always(clk.posedge)
    def write_logic():
        if we:
            RAM[int(iaddr)].next = wd

    @always_comb
    def read_logic():
        rd.next = RAM[int(iaddr)]

    return instances()


if __name__ == '__main__':

    clk = Signal(bool())
    we = Signal(bool())
    addr = Signal(intbv(0, _nrbits=config.DSIZE))
    wd = Signal(intbv(0, _nrbits=config.DSIZE))
    rd = Signal(intbv(0, _nrbits=config.DSIZE))

    dmem_inst = Dmem(clk, we, addr, wd, rd, WORD_SIZE=config.DSIZE, DEPTH=config.RAM_DEPTH)
    dmem_inst.convert(hdl='VHDL')
