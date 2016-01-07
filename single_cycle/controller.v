module controller
(
    input [5:0] op,
    input [5:0] funct,
    output jump,
    output branch,
    output [3:0] aluop,
    output alusrc,
    output regdst,
    output regwrite,
    output memwrite,
    output memtoreg,
    output sextend);

reg [7:0] controls;
reg [3:0] alucontrol;

assign { jump, branch, alusrc, regdst, regwrite, memwrite, memtoreg, sextend} = controls;
assign aluop = alucontrol;

always @(*) begin
    case(op)
        6'b000000: begin // R-type
            controls = 8'b0001100x;
            case(funct)
                6'b100000: alucontrol = 4'b0110; // ADD
                6'b100010: alucontrol = 4'b1110; // SUB
                6'b100100: alucontrol = 4'b0000; // AND
                6'b100101: alucontrol = 4'b0001; // OR
                6'b100110: alucontrol = 4'b0010; // XOR
                6'b100111: alucontrol = 4'b0011; // NOR
                6'b101010: alucontrol = 4'b1111; // SLT
                default: alucontrol = 4'bxxxx;   // function not supported
            endcase
        end
        6'b000010: begin controls = 8'b10xx00xx; alucontrol = 4'bxxxx; end // JUMP (does not use alu)
        6'b000100: begin controls = 8'b010x00xx; alucontrol = 4'b1110; end // BEQ (sub)
        6'b001000: begin controls = 8'b00101001; alucontrol = 4'b0110; end // ADDI
        6'b001010: begin controls = 8'b00101001; alucontrol = 4'b1111; end // SLTI
        6'b001100: begin controls = 8'b00101000; alucontrol = 4'b0000; end // ANDI
        6'b001101: begin controls = 8'b00101000; alucontrol = 4'b0001; end // ORI
        6'b001110: begin controls = 8'b00101000; alucontrol = 4'b0010; end // XORI
        6'b100011: begin controls = 8'b00101011; alucontrol = 4'b0110; end // LW
        6'b101011: begin controls = 8'b001x0101; alucontrol = 4'b0110; end // SW
        default: begin controls = 8'bxxxxxxxx; alucontrol = 4'bxxxx; end // operations not supported
    endcase
end

endmodule // controller
