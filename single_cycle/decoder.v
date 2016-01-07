module decoder
(
    input [5:0] op,
    output jump,
    output branch,
    output alusrc,
    output regdst,
    output regwrite,
    output memwrite,
    output memtoreg,
    output sextend);

reg [7:0] controls;

always @(*) begin
    case(op)
        6'b000000: controls = 8'b0001100x; // R-type
        6'b000010: controls = 8'b10xx00xx; // JUMP
        6'b000100: controls = 8'b010x00xx; // BEQ
        6'b001000: controls = 8'b00101001; // ADDI
        6'b001010: controls = 8'b00101001; // SLTI
        6'b001100: controls = 8'b00101000; // ANDI
        6'b001101: controls = 8'b00101000; // ORI
        6'b001110: controls = 8'b00101000; // XORI
        6'b100011: controls = 8'b00101011; // LW
        6'b101011: controls = 8'b001x0101; // SW
        default: controls = 8'bxxxxxxxx; // operations not supported
    endcase
end
endmodule // decoder
