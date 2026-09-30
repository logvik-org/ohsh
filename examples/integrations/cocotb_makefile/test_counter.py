"""cocotb test for the demo `counter`, shared by both cocotb examples."""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


@cocotb.test()
async def counts_up_after_reset(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    dut.rst.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    dut.rst.value = 0

    for _ in range(5):
        await RisingEdge(dut.clk)
    await Timer(1, units="ns")

    assert int(dut.count.value) == 5, f"expected 5, got {int(dut.count.value)}"
