`timescale 1ns / 1ps

module alu_tb;

reg clk = 1'b0;
always #5 clk = ~clk;

reg [31:0] A = 32'b0;
reg [31:0] B = 32'b0;
reg [2:0] fun = 32'b0;

wire [31:0] Y;
wire C;

always @(posedge clk) begin
	A <= $random;
	B <= $random;
	fun <= A[31:29];
end

always @(negedge clk) begin
	$display("A=%b B= %b fun=%b Y=%b C=%b", A, B, fun, Y, C);
end

initial begin
	#500 $finish;
end

alu #(32) alu1(A, B, fun, Y, C);
endmodule
