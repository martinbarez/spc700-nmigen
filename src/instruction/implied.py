# implied.py: Implied immediate instructions
# Copyright (C) 2021 Martín Bárez <martinbarez>

from nmigen import Module, Signal
from nmigen.asserts import Assert, Past

from alu import Operation
from instruction import Instruction
from registers import add16
from snapshot import Snapshot


# MUL YA    CF      1 9   N-----Z-  YA <- Y*A
class MUL(Instruction):
    opcode = 0xCF

    def synth(core, m: Module):
        for i in range(1, 8):
            with m.If(core.cycle == i):
                m.d.comb += [
                    core.alu.inputa.eq(core.reg.Y),
                    core.alu.inputb.eq(core.reg.A),
                    core.alu.oper.eq(Operation.MUL),
                ]
                m.d.sync += [
                    core.reg.PC.eq(core.reg.PC),
                    core.enable.eq(0),
                    core.addr.eq(core.reg.PC),
                    core.RWB.eq(1),
                    core.cycle.eq(i + 1),
                ]

        with m.If(core.cycle == 8):
            m.d.comb += [
                core.alu.oper.eq(Operation.MUL),
            ]

            m.d.sync += [
                core.reg.Y.eq(core.alu.result),
                core.enable.eq(0),
                core.reg.PC.eq(core.reg.PC),
                core.addr.eq(core.reg.PC),
                core.RWB.eq(1),
                core.cycle.eq(9),
            ]

        with m.If(core.cycle == 9):
            m.d.comb += [
                core.alu.oper.eq(Operation.MUL),
            ]

            m.d.sync += [
                core.reg.A.eq(core.alu.result),
                core.enable.eq(1),
                core.reg.PC.eq(add16(core.reg.PC, 1)),
                core.addr.eq(add16(core.reg.PC, 1)),
                core.RWB.eq(1),
                core.cycle.eq(1),
            ]

    def check(m: Module, data: Snapshot, alu: Signal):
        m.d.comb += [
            Assert(data.read_data[0].matches(MUL.opcode)),
        ]
        for i in range(1, 10):
            m.d.comb += [
                Assert(Past(alu.oper, i) == Operation.MUL),
            ]
        for i in range(3, 10):
            m.d.comb += [
                Assert(Past(alu.inputa, i) == data.pre.Y),
                Assert(Past(alu.inputb, i) == data.pre.A),
            ]
        m.d.comb += [
            Assert(data.post.A == Past(alu.result, 1)),
            Assert(data.post.X == data.pre.X),
            Assert(data.post.Y == Past(alu.result, 2)),
            Assert(data.post.SP == data.pre.SP),
            Assert(data.post.PC == add16(data.pre.PC, 1)),
        ]
        m.d.comb += [
            Assert(data.addresses_read == 1),
            Assert(data.addresses_written == 0),
            Assert(data.read_addr[0] == add16(data.pre.PC, 0)),
        ]


# DIV YA,X      9E      1 12  NV--H-Z-  Y <- YA % X and A <- YA / X
class DIV(Instruction):
    opcode = 0x9E

    def synth(core, m: Module):
        for i in range(1, 11):
            with m.If(core.cycle == i):
                m.d.comb += [
                    core.alu.inputa.eq(core.reg.Y),
                    core.alu.inputb.eq(core.reg.A),
                    core.alu.oper.eq(Operation.DIV),
                ]
                m.d.sync += [
                    core.reg.PC.eq(core.reg.PC),
                    core.enable.eq(0),
                    core.addr.eq(core.reg.PC),
                    core.RWB.eq(1),
                    core.cycle.eq(i + 1),
                ]

        with m.If(core.cycle == 11):
            m.d.comb += [
                core.alu.oper.eq(Operation.DIV),
            ]

            m.d.sync += [
                core.reg.Y.eq(core.alu.result),
                core.enable.eq(0),
                core.reg.PC.eq(core.reg.PC),
                core.addr.eq(core.reg.PC),
                core.RWB.eq(1),
                core.cycle.eq(12),
            ]

        with m.If(core.cycle == 12):
            m.d.comb += [
                core.alu.oper.eq(Operation.DIV),
            ]

            m.d.sync += [
                core.reg.A.eq(core.alu.result),
                core.enable.eq(1),
                core.reg.PC.eq(add16(core.reg.PC, 1)),
                core.addr.eq(add16(core.reg.PC, 1)),
                core.RWB.eq(1),
                core.cycle.eq(1),
            ]

    def check(m: Module, data: Snapshot, alu: Signal):
        m.d.comb += [
            Assert(data.read_data[0].matches(DIV.opcode)),
        ]
        for i in range(1, 13):
            m.d.comb += [
                Assert(Past(alu.oper, i) == Operation.DIV),
            ]
        for i in range(3, 13):
            m.d.comb += [
                Assert(Past(alu.inputa, i) == data.pre.Y),
                Assert(Past(alu.inputb, i) == data.pre.A),
            ]
        m.d.comb += [
            Assert(data.post.A == Past(alu.result, 1)),
            Assert(data.post.X == data.pre.X),
            Assert(data.post.Y == Past(alu.result, 2)),
            Assert(data.post.SP == data.pre.SP),
            Assert(data.post.PC == add16(data.pre.PC, 1)),
        ]
        m.d.comb += [
            Assert(data.addresses_read == 1),
            Assert(data.addresses_written == 0),
            Assert(data.read_addr[0] == add16(data.pre.PC, 0)),
        ]
