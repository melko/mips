all: top_tb.vvp

top_tb.vvp: top_tb.v top.v imem.v dmem.v ../Mips.v
	iverilog -o $@ $^

#mips_tb.vvp: tb/mips mips.v controller.v datapath.v mux2.v regfile.v adder.v sln.v alu.v maindec.v aludec.v flopr.v
clean:
	rm -f tb/*.vvp *.out
