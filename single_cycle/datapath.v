module datapath
(
    input clk,
    input reset,
    // instructions memory signals
    input [31:0] instruction, // comes from instruction memory
    output [31:0] pc, // goes to instruction memory
    // data memory signals
    input [31:0] readdata, // data from data memory
    output [31:0] writedata, // data for data memory
    output [31:0] aluout, // address for data memory
    // control unit signals
    input jump,
    input branch,
    input [3:0] aluop,
    input alusrc,
    input regdst,
    input regwrite,
    input memtoreg,
    input sextend);

wire [31:0] pcnext, pcplus4, pcbranch, pcbranchm, pcjump;
wire [31:0] signimm, signimmsh, unsignimm, immediate;
wire branchgate;

wire [4:0] rfwadd;
wire [31:0] srca, srcb, rfrd2, rfwdata;

wire aluzero;

// next PC logic
flopr #(32) pcreg(clk, reset, pcnext, pc);
adder #(32) pcadd4(pc, 32'b100, pcplus4);
assign pcjump = { pcplus4[31:28], instruction[25:0], 2'b00};

assign signimm = { {(16){instruction[15]}}, instruction[15:0]};
assign unsignimm = { 16'b0, instruction[15:0]};
sln #(32,2) sl2( signimm, signimmsh);
mux2 #(32) signmux( unsignimm, signimm, sextend, immediate);
adder #(32) pcaddimm( signimmsh, pcplus4, pcbranch);
mux2 #(32) branchmux( pcplus4, pcbranch, branchgate ,pcbranchm);
assign branchgate = aluzero & branch;
mux2 #(32) jumpmux( pcbranchm, pcjump, jump, pcnext);


// register file logic
regfile rf(
    .clk(clk), .ra1(instruction[25:21]),
    .ra2(instruction[20:16]), .wa(rfwadd),
    .wd(rfwdata), .we(regwrite),
    .rd1(srca), .rd2(rfrd2));
mux2 #(5) rfwaddmux(instruction[20:16], instruction[15:11], regdst, rfwadd);
mux2 #(32) rfwdatmux(aluout, readdata, memtoreg, rfwdata);

// ALU logic
alu #(32) alu(srca, srcb, aluop, aluout, aluzero);
mux2 #(32) srcbmux(rfrd2, immediate, alusrc, srcb);
assign writedata = rfrd2;

endmodule // datapath
