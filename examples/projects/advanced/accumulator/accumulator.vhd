-- Registered accumulator. It uses the adder from `math_lib` and the register
-- from its own library (`work`), which ohsh maps to the library given with -w.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
library math_lib;

entity accumulator is
  generic (width : positive := 8);
  port (
    clk   : in  std_logic;
    rst   : in  std_logic;
    inc   : in  unsigned(width - 1 downto 0);
    total : out unsigned(width - 1 downto 0)
  );
end entity;

architecture rtl of accumulator is
  signal acc : unsigned(width - 1 downto 0);
  signal nxt : unsigned(width - 1 downto 0);
begin
  add_i : entity math_lib.adder
    generic map (width => width)
    port map (a => acc, b => inc, sum => nxt);

  reg_i : entity work.acc_register
    generic map (width => width)
    port map (clk => clk, rst => rst, d => nxt, q => acc);

  total <= acc;
end architecture;
