-- Register with synchronous reset. It is compiled into the same library as the
-- accumulator, which is why the accumulator's manifest lists it under `work`.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity acc_register is
  generic (width : positive := 8);
  port (
    clk : in  std_logic;
    rst : in  std_logic;
    d   : in  unsigned(width - 1 downto 0);
    q   : out unsigned(width - 1 downto 0)
  );
end entity;

architecture rtl of acc_register is
begin
  process (clk)
  begin
    if rising_edge(clk) then
      if rst = '1' then
        q <= (others => '0');
      else
        q <= d;
      end if;
    end if;
  end process;
end architecture;
