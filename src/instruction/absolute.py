# absolute.py: Absolute address instructions
# Copyright (C) 2021 Martín Bárez <martinbarez>

from nmigen import Cat, Const, Module, Signal
from nmigen.asserts import Assert, Past

from alu import Operation
from instruction import Instruction
from registers import add16
from snapshot import Snapshot


# MOV A, !abs   E5      3 4   N-----Z-  A <- (abs)
class MOV_A_read(Instruction):
    opcode = 0xE5

    def synth(core, m: Module):
        with m.If(core.cycle == 2):
            m.d.comb += core.alu.oper.eq(Operation.NOP)
            m.d.sync += [
                core.tmp.eq(core.dout),
                core.reg.PC.eq(add16(core.reg.PC, 1)),
                core.enable.eq(1),
                core.addr.eq(add16(core.reg.PC, 1)),
                core.RWB.eq(1),
                core.cycle.eq(3),
            ]

        with m.If(core.cycle == 3):
            m.d.comb += core.alu.oper.eq(Operation.NOP)
            m.d.sync += [
                core.reg.PC.eq(core.reg.PC),
                core.enable.eq(1),
                core.addr.eq(Cat(core.tmp, core.dout)),
                core.RWB.eq(1),
                core.cycle.eq(4),
            ]

        with m.If(core.cycle == 4):
            m.d.comb += [
                core.alu.inputa.eq(core.dout),
                core.alu.inputb.eq(Const(0x00)),
                core.alu.oper.eq(Operation.OOR),
            ]
            m.d.sync += [
                core.reg.A.eq(core.alu.result),
                core.reg.PC.eq(add16(core.reg.PC, 1)),
                core.enable.eq(1),
                core.addr.eq(add16(core.reg.PC, 1)),
                core.RWB.eq(1),
                core.cycle.eq(1),
            ]

    def check(m: Module, data: Snapshot, alu: Signal):
        m.d.comb += [
            Assert(data.read_data[0].matches(MOV_A_read.opcode)),
        ]
        m.d.comb += [
            Assert(Past(alu.oper, 4) == Operation.NOP),
            Assert(Past(alu.oper, 3) == Operation.NOP),
            Assert(Past(alu.oper, 2) == Operation.NOP),
            Assert(Past(alu.oper, 1) == Operation.OOR),
            Assert(Past(alu.inputa) == data.read_data[3]),
            Assert(Past(alu.inputb) == 0),
            Assert(Past(alu.result) == data.read_data[3]),
        ]
        m.d.comb += [
            Assert(data.post.A == Past(alu.result)),
            Assert(data.post.X == data.pre.X),
            Assert(data.post.Y == data.pre.Y),
            Assert(data.post.SP == data.pre.SP),
            Assert(data.post.PC == add16(data.pre.PC, 3)),
        ]
        m.d.comb += [
            Assert(data.addresses_read == 4),
            Assert(data.addresses_written == 0),
            Assert(data.read_addr[0] == add16(data.pre.PC, 0)),
            Assert(data.read_addr[1] == add16(data.pre.PC, 1)),
            Assert(data.read_addr[2] == add16(data.pre.PC, 2)),
            Assert(data.read_addr[3] == Cat(data.read_data[1], data.read_data[2])),
        ]


# MOV    !abs, A   C5      3 5   --------  A -> (abs)
class MOV_A_write(Instruction):
    opcode = 0xC5

    def synth(core, m: Module):
        with m.If(core.cycle == 2):
            m.d.comb += core.alu.oper.eq(Operation.NOP)
            m.d.sync += [
                core.tmp.eq(core.dout),
                core.reg.PC.eq(add16(core.reg.PC, 1)),
                core.enable.eq(1),
                core.addr.eq(add16(core.reg.PC, 1)),
                core.RWB.eq(1),
                core.cycle.eq(3),
            ]

        with m.If(core.cycle == 3):
            m.d.comb += core.alu.oper.eq(Operation.NOP)
            m.d.sync += [
                core.reg.PC.eq(core.reg.PC),
                core.enable.eq(1),
                core.addr.eq(Cat(core.tmp, core.dout)),
                core.din.eq(core.reg.A),
                core.RWB.eq(0),
                core.cycle.eq(4),
            ]

        with m.If(core.cycle == 4):
            m.d.comb += core.alu.oper.eq(Operation.NOP)
            m.d.sync += [
                core.reg.PC.eq(core.reg.PC),
                core.enable.eq(0),
                core.addr.eq(core.reg.PC),
                core.RWB.eq(1),
                core.cycle.eq(5),
            ]

        with m.If(core.cycle == 5):
            m.d.comb += core.alu.oper.eq(Operation.NOP)
            m.d.sync += [
                core.reg.PC.eq(add16(core.reg.PC, 1)),
                core.enable.eq(1),
                core.addr.eq(add16(core.reg.PC, 1)),
                core.RWB.eq(1),
                core.cycle.eq(1),
            ]

    def check(m: Module, data: Snapshot, alu: Signal):
        m.d.comb += [
            Assert(data.read_data[0].matches(MOV_A_write.opcode)),
        ]
        m.d.comb += [
            Assert(Past(alu.oper, 5) == Operation.NOP),
            Assert(Past(alu.oper, 4) == Operation.NOP),
            Assert(Past(alu.oper, 3) == Operation.NOP),
            Assert(Past(alu.oper, 2) == Operation.NOP),
            Assert(Past(alu.oper, 1) == Operation.NOP),
        ]
        m.d.comb += [
            Assert(data.post.A == data.pre.A),
            Assert(data.post.X == data.pre.X),
            Assert(data.post.Y == data.pre.Y),
            Assert(data.post.SP == data.pre.SP),
            Assert(data.post.PC == add16(data.pre.PC, 3)),
            Assert(data.post.PSW == data.pre.PSW),
        ]
        m.d.comb += [
            Assert(data.addresses_read == 3),
            Assert(data.addresses_written == 1),
            Assert(data.read_addr[0] == add16(data.pre.PC, 0)),
            Assert(data.read_addr[1] == add16(data.pre.PC, 1)),
            Assert(data.read_addr[2] == add16(data.pre.PC, 2)),
            Assert(data.write_addr[0] == Cat(data.read_data[1], data.read_data[2])),
            Assert(data.write_data[0] == data.pre.A),
        ]


# ADC    A, !abs   85      3 4   NV--H-ZC  A += (abs)        + C
class ADC(Instruction):
    opcode = 0x85

    def synth(core, m: Module):
        with m.If(core.cycle == 2):
            m.d.comb += core.alu.oper.eq(Operation.NOP)
            m.d.sync += [
                core.tmp.eq(core.dout),
                core.reg.PC.eq(add16(core.reg.PC, 1)),
                core.enable.eq(1),
                core.addr.eq(add16(core.reg.PC, 1)),
                core.RWB.eq(1),
                core.cycle.eq(3),
            ]

        with m.If(core.cycle == 3):
            m.d.comb += core.alu.oper.eq(Operation.NOP)
            m.d.sync += [
                core.reg.PC.eq(core.reg.PC),
                core.enable.eq(1),
                core.addr.eq(Cat(core.tmp, core.dout)),
                core.RWB.eq(1),
                core.cycle.eq(4),
            ]

        with m.If(core.cycle == 4):
            m.d.comb += [
                core.alu.inputa.eq(core.reg.A),
                core.alu.inputb.eq(core.dout),
                core.alu.oper.eq(Operation.ADC),
            ]

            m.d.sync += [
                core.reg.A.eq(core.alu.result),
                core.reg.PC.eq(add16(core.reg.PC, 1)),
                core.enable.eq(1),
                core.addr.eq(add16(core.reg.PC, 1)),
                core.RWB.eq(1),
                core.cycle.eq(1),
            ]

    def check(m: Module, data: Snapshot, alu: Signal):
        m.d.comb += [
            Assert(data.read_data[0].matches(ADC.opcode)),
        ]
        m.d.comb += [
            Assert(Past(alu.oper, 4) == Operation.NOP),
            Assert(Past(alu.oper, 3) == Operation.NOP),
            Assert(Past(alu.oper, 2) == Operation.NOP),
            Assert(Past(alu.oper, 1) == Operation.ADC),
            Assert(Past(alu.inputa) == data.pre.A),
            Assert(Past(alu.inputb) == data.read_data[3]),
        ]
        m.d.comb += [
            Assert(data.post.A == Past(alu.result)),
            Assert(data.post.X == data.pre.X),
            Assert(data.post.Y == data.pre.Y),
            Assert(data.post.SP == data.pre.SP),
            Assert(data.post.PC == add16(data.pre.PC, 3)),
        ]
        m.d.comb += [
            Assert(data.addresses_read == 4),
            Assert(data.addresses_written == 0),
            Assert(data.read_addr[0] == add16(data.pre.PC, 0)),
            Assert(data.read_addr[1] == add16(data.pre.PC, 1)),
            Assert(data.read_addr[2] == add16(data.pre.PC, 2)),
            Assert(data.read_addr[3] == Cat(data.read_data[1], data.read_data[2])),
        ]


# JMP    !abs      5F      3 3   --------  PC <- abs     : allows to jump anywhere in the memory space
class JMP(Instruction):
    opcode = 0x5F

    def synth(core, m: Module):
        with m.If(core.cycle == 2):
            m.d.comb += core.alu.oper.eq(Operation.NOP)
            m.d.sync += [
                core.tmp.eq(core.dout),
                core.reg.PC.eq(add16(core.reg.PC, 1)),
                core.enable.eq(1),
                core.addr.eq(add16(core.reg.PC, 1)),
                core.RWB.eq(1),
                core.cycle.eq(3),
            ]

        with m.If(core.cycle == 3):
            m.d.comb += core.alu.oper.eq(Operation.NOP)
            m.d.sync += [
                core.reg.PC.eq(Cat(core.tmp, core.dout)),
                core.enable.eq(1),
                core.addr.eq(Cat(core.tmp, core.dout)),
                core.RWB.eq(1),
                core.cycle.eq(1),
            ]

    def check(m: Module, data: Snapshot, alu: Signal):
        m.d.comb += [
            Assert(data.read_data[0].matches(JMP.opcode)),
        ]
        m.d.comb += [
            Assert(Past(alu.oper, 3) == Operation.NOP),
            Assert(Past(alu.oper, 2) == Operation.NOP),
            Assert(Past(alu.oper, 1) == Operation.NOP),
        ]
        m.d.comb += [
            Assert(data.post.A == data.pre.A),
            Assert(data.post.X == data.pre.X),
            Assert(data.post.Y == data.pre.Y),
            Assert(data.post.SP == data.pre.SP),
            Assert(data.post.PC[:8] == data.read_data[1]),
            Assert(data.post.PC[8:] == data.read_data[2]),
            Assert(data.post.PSW == data.pre.PSW),
        ]
        m.d.comb += [
            Assert(data.addresses_read == 3),
            Assert(data.addresses_written == 0),
            Assert(data.read_addr[0] == add16(data.pre.PC, 0)),
            Assert(data.read_addr[1] == add16(data.pre.PC, 1)),
            Assert(data.read_addr[2] == add16(data.pre.PC, 2)),
        ]
