from myhdl import *

@block
def Regfile(clk, ra1, ra2, wa, wd, we, rd1, rd2, depth=32):

    rf = [Signal(modbv(0)[len(wd):]) for i in range(depth)]

    @always(clk.posedge)
    def seq_logic():
        if we: rf[wa].next = wd

    @always_comb
    def comb_logic():
        rd1.next = rf[ra1] if ra1 else 0
        rd2.next = rf[ra2] if ra2 else 0


    return instances()

if __name__ == '__main__':
    clk = Signal(bool())
    ra1 = Signal(modbv(0)[5:])
    ra2 = Signal(modbv(0)[5:])
    wa = Signal(modbv(0)[5:])
    wd = Signal(modbv(0)[32:])
    we = Signal(bool())
    rd1 = Signal(modbv(0)[32:])
    rd2 = Signal(modbv(0)[32:])

    regfile_inst = Regfile(clk, ra1, ra2, wa, wd, we, rd1, rd2)
    regfile_inst.convert(hdl='VHDL')
