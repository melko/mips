module top_tb();

reg clk;
reg reset;

wire [31:0] writedata, dataadr;
wire memwrite;

top dut(clk, reset, writedata, dataadr, memwrite);

initial begin
	reset <= 1;
	#22;
	reset <= 0;
end

always begin
	clk <= 1;
	#5;
	clk <= 0;
	#5;
end

always @(negedge clk) begin
	if(memwrite) begin
		if(dataadr===84 & writedata===7) begin
			$display("Simulation succeeded");
			$finish;
		end else if(dataadr !== 80) begin
			$display("Simulation failed");
			$display("%d %d", dataadr, writedata);
			$finish;
		end
	end
end

endmodule
