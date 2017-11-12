from myhdl import *
import config

ALU_OPS = enum(
    'A_AND_B',
    'A_OR_B',
    'A_XOR_B',
    'A_NOR_B',
    'A_PLUS_B',
    'SLT',
)

def decode_op(op):
    decoded_op = ALU_OPS.A_AND_B

    if   op == 0b000: decoded_op = ALU_OPS.A_AND_B
    elif op == 0b001: decoded_op = ALU_OPS.A_OR_B
    elif op == 0b010: decoded_op = ALU_OPS.A_XOR_B
    elif op == 0b011: decoded_op = ALU_OPS.A_NOR_B
    elif op == 0b110: decoded_op = ALU_OPS.A_PLUS_B
    elif op == 0b111: decoded_op = ALU_OPS.SLT

    return decoded_op

@block
def ALU(A, B, fun, Y, zero):

    """ A simple ALU

    A -- in vec - first operand
    B -- in vec - second operand
    fun -- in vec - function selector
    Y -- out vec - result
    zero -- out - result is zero

    """

    result = Signal(modbv(0, _nrbits=config.DSIZE))
    BB = Signal(modbv(0, _nrbits=config.DSIZE))
    res = fun(len(fun) - 1)
    op = fun(len(fun) - 1, 0)
    tmp_sum = Signal(modbv(Y.val))

    @always_comb
    def logic():
        decoded_op = decode_op(op)

        if decoded_op == ALU_OPS.A_AND_B:
            result.next = A & BB
        elif decoded_op == ALU_OPS.A_OR_B:
            result.next = A | BB
        elif decoded_op == ALU_OPS.A_XOR_B:
            result.next = A ^ BB
        elif decoded_op == ALU_OPS.A_NOR_B:
            result.next = ~(A | BB)
        elif decoded_op == ALU_OPS.A_PLUS_B:
            result.next = (A + BB + res)
        elif decoded_op == ALU_OPS.SLT:
            result.next = tmp_sum[31]

    @always_comb
    def logic2():
        BB.next = ~B if res else B
        zero.next = 1 if result == 0 else 0
        Y.next = result

    @always_comb
    def logic3():
        tmp_sum.next = A + BB + res

    return instances()

if __name__ == '__main__':
    A = Signal(modbv(0, _nrbits=config.DSIZE))
    B = Signal(modbv(0, _nrbits=config.DSIZE))
    fun = Signal(modbv(0, _nrbits=config.ALU_FUN_SIZE))
    Y = Signal(modbv(0, _nrbits=config.DSIZE))
    zero = Signal(bool())

    ALU_inst = ALU(A, B, fun, Y, zero)
    ALU_inst.convert(hdl='VHDL')
