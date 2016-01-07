module aludec
(
    input [5:0] op,
    input [5:0] funct,
    output reg [3:0] aluop);

always @(*) begin
    case(op)
        6'b000000: case(funct) // R-type instructions
            6'b100000: aluop = 4'b0110; // ADD
            6'b100010: aluop = 4'b1110; // SUB
            6'b100100: aluop = 4'b0000; // AND
            6'b100101: aluop = 4'b0001; // OR
            6'b100110: aluop = 4'b0010; // XOR
            6'b100111: aluop = 4'b0011; // NOR
            6'b101010: aluop = 4'b1111; // SLT
            default: aluop = 4'bxxxx;   // function not supported
        endcase
        6'b000010: aluop = 4'bxxxx; // JUMP does not use alu
        6'b000100: aluop = 4'b1110; // SUB for BEQ
        6'b001000: aluop = 4'b0110; // ADD for ADDI
        6'b001010: aluop = 4'b1111; // SLT for SLTI
        6'b001100: aluop = 4'b0000; // AND for ANDI
        6'b001101: aluop = 4'b0001; // OR for ORI
        6'b001110: aluop = 4'b0010; // XOR for XORI
        6'b10x011: aluop = 4'b0110; // ADD for LW and SW
        default: aluop = 4'bxxxx; // operations not supported
    endcase
end

endmodule // aludec
