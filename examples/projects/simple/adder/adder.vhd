-- Combinational adder, compiled into library `math_lib`.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity adder is
  generic (width : positive := 8);
  port (
    a   : in  unsigned(width - 1 downto 0);
    b   : in  unsigned(width - 1 downto 0);
    sum : out unsigned(width - 1 downto 0)
  );
end entity;

architecture rtl of adder is
begin
  sum <= a + b;
end architecture;
