from myhdl import *
import config

@block
def Regfile(clk, ra1, ra2, wa, wd, we, rd1, rd2, DEPTH=32):
    """ Register file, implemented as a RAM with 2 async read ports and one clocked write port
    reading from register 0 always returns 0

    clk -- in - clock signal
    ra1 -- in vec - read address for port1
    ra2 -- in vec - read address for port2
    wa -- in vec - write address
    wd -- in vec - write data
    we -- in - write enable

    rd1 -- out vec - read data port1
    rd2 -- out vec - read data port2

    """

    rf = [Signal(intbv(0, _nrbits=config.DSIZE)) for i in range(DEPTH)]

    @always(clk.posedge)
    def seq_logic():
        if we: rf[wa].next = wd

    @always_comb
    def comb_logic():
        rd1.next = rf[ra1] if ra1 else 0 # return 0 when accessing $0
        rd2.next = rf[ra2] if ra2 else 0


    return instances()

if __name__ == '__main__':
    clk = Signal(bool())
    ra1 = Signal(intbv(0, _nrbits=config.REG_ASIZE))
    ra2 = Signal(intbv(0, _nrbits=config.REG_ASIZE))
    wa = Signal(intbv(0, _nrbits=config.REG_ASIZE))
    wd = Signal(intbv(0, _nrbits=config.DSIZE))
    we = Signal(bool())
    rd1 = Signal(intbv(0, _nrbits=config.DSIZE))
    rd2 = Signal(intbv(0, _nrbits=config.DSIZE))

    regfile_inst = Regfile(clk, ra1, ra2, wa, wd, we, rd1, rd2, DEPTH=config.NUM_REGS)
    regfile_inst.convert(hdl='VHDL')
