// Up-counter configured by the macros in counter_defs.vh.
module counter (
    input  wire                      clk,
    input  wire                      rst,
    output reg  [`COUNTER_WIDTH-1:0] count
);
  always @(posedge clk) begin
    if (rst) count <= {`COUNTER_WIDTH{1'b0}};
    else count <= count + `COUNTER_STEP;
  end
endmodule
