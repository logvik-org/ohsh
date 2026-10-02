-- UVVM testbench for the `accumulator` of both example projects. Compile it into
-- the same library as the accumulator, after UVVM's uvvm_util library.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library uvvm_util;
context uvvm_util.uvvm_util_context;

use std.env.all;

entity tb_accumulator_uvvm is
end entity;

architecture sim of tb_accumulator_uvvm is
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

  main : process
  begin
    set_log_file_name("uvvm_log.txt");
    log(ID_LOG_HDR, "Accumulator UVVM testbench");

    rst <= '1';
    inc <= to_unsigned(0, width);
    wait until rising_edge(clk);
    rst <= '0';
    inc <= to_unsigned(3, width);
    for i in 1 to 4 loop
      wait until rising_edge(clk);
    end loop;
    wait for 1 ns;

    check_value(to_integer(total), 12, ERROR, "accumulator total after four +3 steps");

    report_alert_counters(FINAL);
    log(ID_LOG_HDR, "SIMULATION COMPLETED");
    finish;
  end process;
end architecture;
