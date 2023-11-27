// This is ChatGPT-generated code with minor modifications meant only as a demo sample. No rights belong to us. 

module traffic_light (
  input wire clk,      // Clock input
  input wire rst,      // Reset input
  output reg red,      // Red light output
  output reg yellow,   // Yellow light output
  output reg green     // Green light output
);

  // Define states
  reg [1:0] current_state, next_state;

  // State transition and output logic
  always @(posedge clk or posedge rst) begin
    if (rst) begin
      // Initialize to RED state on reset
      current_state <= 2'b00;
    end else begin
      // State transition logic
      current_state <= next_state;
    end
  end

  // Next state and output logic
  always @* begin
    case (current_state)
      2'b00: begin // RED
        next_state = 2'b01; // Transition to GREEN
        {red, yellow, green} = 3'b100;
      end
      2'b01: begin // GREEN
        next_state = 2'b10; // Transition to YELLOW
        {red, yellow, green} = 3'b001;
      end
      2'b10: begin // YELLOW
        next_state = 2'b00; // Transition to RED
        {red, yellow, green} = 3'b010;
      end
      default: begin // Default to RED
        next_state = 2'b00;
        {red, yellow, green} = 3'b100;
      end
    endcase
  end

endmodule