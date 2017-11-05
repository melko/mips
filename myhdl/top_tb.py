from myhdl import *
from mips import Mips
from dmem import Dmem
from imem import Imem


def read_file(memfile):
    with open(memfile, "r") as f:
        data = f.readlines()
    data = list(map(lambda x: int(x.strip(), 16), data))
    return tuple(data)

@block
def Top(clk, reset, writedata, daddr, memwrite, ROM, dmem_depth=64, word_size=32):

    pc = Signal(modbv(0)[word_size:])
    instr = Signal(modbv(0)[word_size:])
    readdata = Signal(modbv(0)[word_size:])

    mips_inst = Mips(clk, reset, pc, instr, memwrite, daddr, writedata, readdata)
    imem_inst = Imem(pc(8, 2), instr, ROM)
    dmem_inst = Dmem(clk, memwrite, daddr, writedata, readdata, dmem_depth)

    return instances()

@block
def tb_top():

    dmem_depth = 128
    word_size = 32
    memfile = "memfile.dat"
    clk_period = 10

    ROM = read_file(memfile)

    clk = Signal(bool())
    reset = ResetSignal(1, active=1, async=True)

    writedata = Signal(modbv(0)[word_size:])
    daddr = Signal(modbv(0)[word_size:])
    memwrite = Signal(bool())

    top_inst = Top(clk, reset, writedata, daddr, memwrite, ROM, dmem_depth, word_size)

    @instance
    def drive_clk():
        while True:
            clk.next = not clk
            yield delay(clk_period // 2)

    @instance
    def drive_reset():
        reset.next = 1
        yield delay(5 * clk_period)
        reset.next = 0

    @always(clk.posedge)
    def check_result():
        if memwrite and daddr == 84:
            if writedata == 7:
                print("Simulation succeded")
                raise StopSimulation()
            else:
                print("Simulation failed, writedata = %s" % writedata)
                raise StopSimulation()

    return instances()

if __name__ == '__main__':
    tb = tb_top()
    conversion.verify.simulator = 'ghdl'
    #conversion.verify(tb)
    sim = Simulation(tb_top()).run()
