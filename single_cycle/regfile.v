module regfile(
	input         clk,
	input  [4:0]  ra1,
	input  [4:0]  ra2,
	input  [4:0]  wa,
	input  [31:0] wd,
	input         we,
	output [31:0] rd1,
	output [31:0] rd2
);

reg [31:0] rf[31:0];

// write ports are written on clk rising edge
always @(posedge clk)
	if(we) rf[wa] <= wd;

// read ports are read combinationally
assign rd1 = (ra1 != 0) ? rf[ra1] : 0;
assign rd2 = (ra2 != 0) ? rf[ra2] : 0;

endmodule
