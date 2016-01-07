all: top_tb.vvp regfile_tb.vvp alu_tb.vvp

top_tb.vvp: tb/top_tb.v tb/top.v tb/imem.v tb/dmem.v mips.v datapath.v controller.v flopr.v adder.v sln.v mux2.v regfile.v alu.v
	iverilog -o tb/top_tb.vvp tb/top_tb.v tb/top.v tb/imem.v tb/dmem.v mips.v datapath.v controller.v flopr.v adder.v sln.v mux2.v regfile.v alu.v

regfile_tb.vvp: tb/regfile_tb.v regfile.v
	iverilog -o tb/regfile_tb.vvp tb/regfile_tb.v regfile.v

alu_tb.vvp: tb/alu_tb.v alu.v mux2.v
	iverilog -o tb/alu_tb.vvp tb/alu_tb.v alu.v mux2.v

#mips_tb.vvp: tb/mips mips.v controller.v datapath.v mux2.v regfile.v adder.v sln.v alu.v maindec.v aludec.v flopr.v
clean:
	rm -f tb/*.vvp *.out
