module sln #(
	parameter WIDTH = 32,
	parameter SHIFT = 2
)
(
	input [WIDTH-1:0] X,
	output [WIDTH-1:0] Y
);

assign Y = { X[WIDTH-SHIFT-1:0], {(SHIFT){1'b0}} };
endmodule
