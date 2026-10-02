-- Registered accumulator built from the adder in the same library.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

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
  signal acc : unsigned(width - 1 downto 0) := (others => '0');
  signal nxt : unsigned(width - 1 downto 0);
begin
  add_i : entity work.adder
    generic map (width => width)
    port map (a => acc, b => inc, sum => nxt);

  process (clk)
  begin
    if rising_edge(clk) then
      if rst = '1' then
        acc <= (others => '0');
      else
        acc <= nxt;
      end if;
    end if;
  end process;

  total <= acc;
end architecture;
