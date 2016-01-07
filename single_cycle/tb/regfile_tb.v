`timescale 1ns / 1ps

module regfile_tb;

reg clk = 1'b0;
always #5 clk = ~clk;

reg  [4:0]  ra1 = 5'h00;
reg  [4:0]  ra2 = 5'h00;
wire [31:0] rd1;
wire [31:0] rd2;

reg we        = 1'b0;
reg [4:0]  wa = 5'h00;
reg [31:0] wd = 32'hffffffff;

always @(posedge clk) begin
	wa <= wa + 1;
	wd <= wd - 1;
end

always @(posedge clk) begin
	if(we == 0) begin
		ra1 <= ra1 + 1;
		ra2 <= ra2 + 1;
	end
end

initial begin
	#2 we <= 1;
	#330 we <= 0;
	#500 $finish;
end

initial begin
	$monitor("ra1=%d val=%h ra2=%d val=%h", ra1, rd1, ra2, rd2);
end

regfile rf(
	.clk(clk),
	.ra1(ra1),
	.ra2(ra2),
	.wa(wa),
	.wd(wd),
	.we(we),
	.rd1(rd1),
	.rd2(rd2)
);
endmodule
