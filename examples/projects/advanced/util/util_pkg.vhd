-- Helpers shared across libraries. The manifests compile this into `util_lib`.
library ieee;
use ieee.numeric_std.all;

package util_pkg is
  -- Adds a and b (same width) and clamps at the largest value instead of wrapping.
  function saturating_add(a, b : unsigned) return unsigned;
end package;

package body util_pkg is
  function saturating_add(a, b : unsigned) return unsigned is
    constant width    : natural := a'length;
    constant all_ones : unsigned(width - 1 downto 0) := (others => '1');
    variable wide     : unsigned(width downto 0);
  begin
    wide := resize(a, width + 1) + resize(b, width + 1);
    if wide(width) = '1' then
      return all_ones;
    end if;
    return wide(width - 1 downto 0);
  end function;
end package body;
