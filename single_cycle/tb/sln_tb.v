module sln_tb;

reg clk = 1'b0;
always #5 clk = ~clk;

reg [31:0] X = 32'b0;
wire [31:0] Y;

always @(posedge clk) begin
	X <= X + 1;
end

always @(negedge clk) begin
	$display("X=%b Y=%b", X, Y);
end

initial begin
	#200 $finish;
end

sln #(32,2) sl2(X,Y);

endmodule
