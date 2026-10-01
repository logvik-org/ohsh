-- VUnit testbench for the `accumulator` of both example projects. run.py adds
-- it to the same library as the accumulator, so `work.accumulator` finds it.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library vunit_lib;
context vunit_lib.vunit_context;

entity tb_accumulator_vunit is
  generic (runner_cfg : string);
end entity;

architecture sim of tb_accumulator_vunit is
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
    test_runner_setup(runner, runner_cfg);

    rst <= '1';
    inc <= to_unsigned(0, width);
    wait until rising_edge(clk);
    rst <= '0';
    inc <= to_unsigned(3, width);
    for i in 1 to 4 loop
      wait until rising_edge(clk);
    end loop;
    wait for 1 ns;

    check_equal(to_integer(total), 12, "accumulator total after four +3 steps");

    test_runner_cleanup(runner);
  end process;

  test_runner_watchdog(runner, 1 us);
end architecture;
