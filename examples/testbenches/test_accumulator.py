"""cocotb test for the VHDL `accumulator` of both example projects."""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


@cocotb.test()
async def adds_increment_every_clock(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())

    dut.rst.value = 1
    dut.inc.value = 0
    await RisingEdge(dut.clk)
    dut.rst.value = 0
    dut.inc.value = 3

    for _ in range(4):
        await RisingEdge(dut.clk)
    await Timer(1, unit="ns")

    assert int(dut.total.value) == 12, f"expected 12, got {int(dut.total.value)}"
