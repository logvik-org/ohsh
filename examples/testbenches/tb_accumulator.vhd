-- Self-checking testbench for the demo `accumulator`, for use with GHDL/NVC.
-- The design sources (adder, accumulator) come from ohsh-generated .src lists;
-- this testbench is compiled on top of them into the `work` library.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.env.all;

entity tb_accumulator is
end entity;

architecture sim of tb_accumulator is
  constant width : positive := 8;
  signal clk   : std_logic := '0';
  signal rst   : std_logic := '1';
  signal inc   : unsigned(width - 1 downto 0) := (others => '0');
  signal total : unsigned(width - 1 downto 0);
begin
  dut : entity work.accumulator
    generic map (width => width)
    port map (clk => clk, rst => rst, inc => inc, total => total);

  clk <= not clk after 5 ns;

  stim : process
  begin
    rst <= '1';
    inc <= to_unsigned(0, width);
    wait until rising_edge(clk);          -- rst sampled high: acc stays 0
    rst <= '0';
    inc <= to_unsigned(3, width);
    for i in 1 to 4 loop                  -- four +3 steps => 12
      wait until rising_edge(clk);
    end loop;
    wait for 1 ns;
    assert total = to_unsigned(12, width)
      report "FAIL: expected 12, got " & integer'image(to_integer(total))
      severity failure;
    report "PASS: accumulator total = 12" severity note;
    finish;
  end process;
end architecture;
