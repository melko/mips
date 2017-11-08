enum instruction_type {
	RTYPE_INSTR = 0,
	JUMP_INSTR = 2,
	BEQ_INSTR = 4,
	ADDI_INSTR = 8,
	SLTI_INSTR = 10,
	ANDI_INSTR = 12,
	ORI_INSTR = 13,
	XORI_INSTR = 14,
	LW_INSTR = 35,
	SW_INSTR = 43,
};

enum funct_type {
	ADD_INSTR = 32,
	SUB_INSTR = 34,
	AND_INSTR = 36,
	OR_INSTR = 37,
	XOR_INSTR = 38,
	NOR_INSTR = 39,
	SLT_INSTR = 42,
};

void __kernel mips(__constant uint* imem, __global int* rf, __global int* dmem)
{
	uint pc = 0;
	printf("Init\n");

	while (1) {
		uint instruction = imem[pc >> 2];
		uchar op = (instruction >> 26) & 0x3f;
		uchar rs = (instruction >> 21) & 0x1f;
		uchar rt = (instruction >> 16) & 0x1f;
		uchar rd = (instruction >> 11) & 0x1f;
		uchar sa = (instruction >> 6) & 0x1f;
		uchar funct = instruction & 0x3f;
		ushort imm = instruction & 0xffff;
		short s_imm = imm;
		uint target = instruction & 0x3ffffff;

		pc += 4;
		rf[0] = 0; // $0 must always return 0

		switch (op) {
			case RTYPE_INSTR:
				switch (funct) {
					case ADD_INSTR:
						rf[rd] = rf[rs] + rf[rt];
						break;
					case SUB_INSTR:
						rf[rd] = rf[rs] - rf[rt];
						break;
					case AND_INSTR:
						rf[rd] = rf[rs] & rf[rt];
						break;
					case OR_INSTR:
						rf[rd] = rf[rs] | rf[rt];
						break;
					case XOR_INSTR:
						rf[rd] = rf[rs] ^ rf[rt];
						break;
					case NOR_INSTR:
						rf[rd] = ~(rf[rs] | rf[rt]);
						break;
					case SLT_INSTR:
						rf[rd] = (rf[rs] < rf[rt]) ? 1 : 0;
						break;
					default:
						printf("invalid funct %x from opcode %.8x, halting\n", funct, instruction);
						return;
				}
				break;
			case JUMP_INSTR:
				pc = (pc & 0xf0000000) | (target << 2);
				break;
			case BEQ_INSTR:
				if (rf[rs] == rf[rt])
					pc += s_imm << 2;
				break;
			case ADDI_INSTR:
				rf[rt] = rf[rs] + s_imm;
				break;
			case SLTI_INSTR:
				rf[rt] = (rf[rs] < s_imm) ? 1 : 0;
				break;
			case ANDI_INSTR:
				rf[rt] = rf[rs] & imm;
				break;
			case ORI_INSTR:
				rf[rt] = rf[rs] | imm;
				break;
			case XORI_INSTR:
				rf[rt] = rf[rs] ^ imm;
				break;
			case LW_INSTR:
				rf[rt] = dmem[(s_imm + rf[rs]) >> 2];
				break;
			case SW_INSTR:
				dmem[(s_imm + rf[rs]) >> 2] = rf[rt];
				break;
			default:
				printf("Invalid opcode from instruction %.8x, halting\n", instruction);
				return;
		}
	}
}
