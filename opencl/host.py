#!/usr/bin/env python
import numpy
import pyopencl as cl

memfile = "memfile.dat"
kernel = "mips.cl"

with open(memfile, "r") as f:
    instructions = f.readlines()

instructions = numpy.array(list(map(lambda x: int(x.strip(), 16), instructions)), dtype=numpy.uint32)

with open(kernel, "r") as f:
    kernel_source = f.read()

rf = numpy.array([0 for i in range(32)], dtype=numpy.int32)
dmem = numpy.array([0 for i in range(128)], dtype=numpy.int32)


context = cl.create_some_context()
queue = cl.CommandQueue(context)
program = cl.Program(context, kernel_source).build()

dev_imem = cl.Buffer(context, cl.mem_flags.COPY_HOST_PTR, hostbuf=instructions)
dev_rf = cl.Buffer(context, cl.mem_flags.COPY_HOST_PTR, hostbuf=rf)
dev_dmem = cl.Buffer(context, cl.mem_flags.COPY_HOST_PTR, hostbuf=dmem)

program.mips(queue, (1,), None, dev_imem, dev_rf, dev_dmem)
cl.enqueue_read_buffer(queue, dev_dmem, dmem).wait()

if dmem[84>>2] == 7:
    print("Success")
else:
    print("Failure")
