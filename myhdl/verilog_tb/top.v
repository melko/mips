module top
(
	input clk,
	input reset,
	output [31:0] writedata,
	output [31:0] dataadr,
	output memwrite);

wire [31:0] pc, instr, readdata;

Mips mips(clk, reset, pc, instr, memwrite, dataadr, writedata, readdata);
imem imem(pc[7:2], instr);
dmem dmem(clk, memwrite, dataadr, writedata, readdata);

endmodule
