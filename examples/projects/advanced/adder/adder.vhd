-- Saturating adder. The manifests compile this into `math_lib`, and it uses the
-- package from `util_lib`.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
library util_lib;
use util_lib.util_pkg.all;

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
  sum <= saturating_add(a, b);
end architecture;
