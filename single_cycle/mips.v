module mips
(
	input clk,
	input reset,
	output [31:0] pc,
	input [31:0] instr,
	output memwrite,
	output [31:0] aluout,
	output [31:0] writedata,
	input [31:0] readdata);

wire memtoreg, alusrc, regdst, regwrite, jump, branch, sextend;
wire [3:0] aluop;

controller c(.op(instr[31:26]), .funct(instr[5:0]), .jump(jump),
	.branch(branch), .aluop(aluop), .alusrc(alusrc), .regdst(regdst), .regwrite(regwrite), .memwrite(memwrite),
	.memtoreg(memtoreg), .sextend(sextend));

datapath dp(.clk(clk), .reset(reset), .instruction(instr), .pc(pc),
	.readdata(readdata), .writedata(writedata), .aluout(aluout), .jump(jump), .branch(branch), .aluop(aluop),
	.alusrc(alusrc), .regdst(regdst), .regwrite(regwrite), .memtoreg(memtoreg), .sextend(sextend));

endmodule
