module mux2 #(parameter WIDTH=32)(
	input [WIDTH-1:0] d0,
	input [WIDTH-1:0] d1,
	input              s,
	output [WIDTH-1:0] Y
);

assign Y = s ? d1 : d0;

endmodule
