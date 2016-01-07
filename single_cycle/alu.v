module alu #(parameter WIDTH = 32)(
	input [WIDTH-1:0]  A,
	input [WIDTH-1:0]  B,
	input [3:0]      fun,
	output [WIDTH-1:0] Y,
	output          zero);

wire [WIDTH-1:0] BB;
wire [WIDTH-1:0] tmp_and;
wire [WIDTH-1:0] tmp_or;
wire [WIDTH-1:0] tmp_xor;
wire [WIDTH-1:0] tmp_nor;
wire [WIDTH-1:0] tmp_sum;
reg  [WIDTH-1:0] result;

mux2 #(WIDTH) m1(B, ~B, fun[3], BB);

assign tmp_and = A & BB;
assign tmp_or  = A | BB;
assign tmp_xor = A ^ BB;
assign tmp_nor = ~tmp_or;
assign tmp_sum = A + BB + fun[3];
assign zero    = (result == 32'b0);

assign Y = result;

always @(*) begin
	case(fun[2:0])
		3'b000: result = tmp_and;
		3'b001: result = tmp_or;
		3'b010: result = tmp_xor;
		3'b011: result = tmp_nor;
		3'b110: result = tmp_sum[WIDTH-1:0];
		3'b111: result = { {(WIDTH-1){1'b0}}, tmp_sum[WIDTH-1]};
		default: result = 32'bx;
	endcase
end

endmodule
