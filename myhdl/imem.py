from myhdl import *

@block
def Imem(addr, rd, ROM):

    """ A simple memory

    clk -- in
    addr -- in vec - read/write address
    rd -- out vec - data to be read

    """

    @always_comb
    def read_logic():
        rd.next = ROM[int(addr)]

    return instances()


if __name__ == '__main__':
    addr = Signal(modbv(0)[32:])
    rd = Signal(modbv(0)[32:])
    ROM = tuple(range(64))

    imem_inst = Imem(addr, rd, ROM)
    imem_inst.convert(hdl='VHDL')
