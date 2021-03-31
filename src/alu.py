# alu.py: A big endian ALU and a module that converts it to little. self checking
# Copyright (C) 2021 Martín Bárez <martinbarez>

from enum import Enum
from typing import List, Optional

from nmigen import Cat, Const, Elaboratable, Module, ResetSignal, Signal
from nmigen.asserts import Assert, Assume, Initial
from nmigen.build import Platform
from nmigen.cli import main_parser, main_runner
from nmigen.sim import Simulator

from registers import Status


class Operation(Enum):
    NOP = 0x0
    ADC = 0x1
    SBC = 0x2
    CMP = 0x3
    AND = 0x4
    OOR = 0x5  # also for MOV with inputb as zero
    EOR = 0x6
    INC = 0x7
    DEC = 0x8
    ASL = 0x9
    LSR = 0xA
    ROL = 0xB
    ROR = 0xC
    XCN = 0xD
    DAA = 0xE
    DAS = 0xF


# TODO
# 16-bit Data Transmission Operations
# 16-bit Arithmetic Operations
# Multiplication/Division Operations
# Bit Operations


class ALU_big(Elaboratable):
    def __init__(self, verification: Operation = None):
        self.inputa = Signal(8)
        self.inputb = Signal(8)
        self.result = Signal(8)
        self.oper = Signal(Operation)

        self.PSW = Status()

        self.result = Signal().like(self.result)
        self._psw = Status()

        self.verification = verification

    def ports(self) -> List[Signal]:
        return [self.inputa, self.inputb, self.oper, self.result]

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        m.d.sync += self.PSW.eq(self._psw)
        m.d.comb += self._psw.eq(self.PSW)

        with m.Switch(self.oper):
            with m.Case(Operation.NOP):
                if self.verification is Operation.NOP:
                    with m.If(~Initial()):
                        m.d.comb += [
                            Assert(self._psw.N == self.PSW.N),
                            Assert(self._psw.V == self.PSW.V),
                            Assert(self._psw.P == self.PSW.P),
                            Assert(self._psw.B == self.PSW.B),
                            Assert(self._psw.H == self.PSW.H),
                            Assert(self._psw.I == self.PSW.I),
                            Assert(self._psw.Z == self.PSW.Z),
                            Assert(self._psw.C == self.PSW.C),
                        ]

            with m.Case(Operation.ADC):
                low = Cat(self.result[:4], self._psw.H)
                high = Cat(self.result[4:], self._psw.C)

                m.d.comb += [
                    low.eq(self.inputa[:4] + self.inputb[:4] + self.PSW.C),
                    high.eq(self.inputa[4:] + self.inputb[4:] + self._psw.H),
                    self._psw.N.eq(self.result.as_signed() < 0),
                    self._psw.Z.eq(self.result == 0),
                    self._psw.V.eq(self.result[7] != self._psw.C),
                ]
                if self.verification is Operation.ADC:
                    r = Signal(8)
                    f = Signal(9)
                    h = Signal(5)
                    m.d.comb += [
                        r.eq(
                            self.inputa.as_signed()
                            + self.inputb.as_signed()
                            + self.PSW.C
                        ),
                        f.eq(self.inputa + self.inputb + self.PSW.C),
                        h.eq(self.inputa[:4] + self.inputb[:4] + self.PSW.C),
                    ]
                    with m.If(~Initial()):
                        m.d.comb += [
                            Assert(self.result == r),
                            Assert(self.result == f[:8]),
                            Assert(self._psw.N == f[7]),
                            Assert(self._psw.V == (f[7] ^ f[8])),
                            Assert(self._psw.P == self.PSW.P),
                            Assert(self._psw.B == self.PSW.B),
                            Assert(self._psw.H == h[4]),
                            Assert(self._psw.I == self.PSW.I),
                            Assert(self._psw.Z == ~(f[:8].bool())),
                            Assert(self._psw.C == f[8]),
                        ]

            with m.Case(Operation.SBC):
                low = Cat(self.result[:4], self._psw.H)
                high = Cat(self.result[4:], self._psw.C)

                m.d.comb += [
                    low.eq(self.inputa[:4] - self.inputb[:4] - self.PSW.C),
                    high.eq(self.inputa[4:] - self.inputb[4:] - self._psw.H),
                    self._psw.N.eq(self.result.as_signed() < 0),
                    self._psw.Z.eq(self.result == 0),
                    self._psw.V.eq(self.result[7] != self._psw.C),
                ]
                if self.verification is Operation.SBC:
                    r = Signal(8)
                    f = Signal(9)
                    h = Signal(5)
                    m.d.comb += [
                        r.eq(
                            self.inputa.as_signed()
                            - self.inputb.as_signed()
                            - self.PSW.C
                        ),
                        f.eq(self.inputa - self.inputb - self.PSW.C),
                        h.eq(self.inputa[:4] - self.inputb[:4] - self.PSW.C),
                    ]
                    with m.If(~Initial()):
                        m.d.comb += [
                            Assert(self.result == r),
                            Assert(self.result == f[:8]),
                            Assert(self._psw.N == f[7]),
                            Assert(self._psw.V == (f[7] ^ f[8])),
                            Assert(self._psw.P == self.PSW.P),
                            Assert(self._psw.B == self.PSW.B),
                            Assert(self._psw.H == h[4]),
                            Assert(self._psw.I == self.PSW.I),
                            Assert(self._psw.Z == ~(f[:8].bool())),
                            Assert(self._psw.C == f[8]),
                        ]

            with m.Case(Operation.CMP):
                full = Cat(self.result, self._psw.C)

                m.d.comb += [
                    full.eq(self.inputa.as_signed() - self.inputb.as_signed()),
                    self._psw.N.eq(self.result.as_signed() < 0),
                    self._psw.Z.eq(self.result == 0),
                    self._psw.V.eq(self.result[7] != self._psw.C),
                ]
                if self.verification is Operation.CMP:
                    r = Signal(9)
                    m.d.comb += r.eq(self.inputa.as_signed() - self.inputb.as_signed())
                    with m.If(~Initial()):
                        m.d.comb += [
                            Assert(self.result == r[:8]),
                            Assert(self._psw.N == r[7]),
                            Assert(self._psw.V == (r[7] ^ r[8])),
                            Assert(self._psw.P == self.PSW.P),
                            Assert(self._psw.B == self.PSW.B),
                            Assert(self._psw.H == self.PSW.H),
                            Assert(self._psw.I == self.PSW.I),
                            Assert(self._psw.Z == ~(r[:8].bool())),
                            Assert(self._psw.C == r[8]),
                        ]

            with m.Case(Operation.AND):
                m.d.comb += [
                    self.result.eq(self.inputa & self.inputb),
                    self._psw.N.eq(self.result.as_signed() < 0),
                    self._psw.Z.eq(self.result == 0),
                ]
                if self.verification is Operation.AND:
                    r = Signal(8)
                    m.d.comb += r.eq(self.inputa & self.inputb)
                    with m.If(~Initial()):
                        m.d.comb += [
                            Assert(self.result == r),
                            Assert(self._psw.N == r[7]),
                            Assert(self._psw.V == self.PSW.V),
                            Assert(self._psw.P == self.PSW.P),
                            Assert(self._psw.B == self.PSW.B),
                            Assert(self._psw.H == self.PSW.H),
                            Assert(self._psw.I == self.PSW.I),
                            Assert(self._psw.Z == ~(r.bool())),
                            Assert(self._psw.C == self.PSW.C),
                        ]

            with m.Case(Operation.OOR):
                m.d.comb += [
                    self.result.eq(self.inputa | self.inputb),
                    self._psw.N.eq(self.result.as_signed() < 0),
                    self._psw.Z.eq(self.result == 0),
                ]
                if self.verification is Operation.OOR:
                    r = Signal(8)
                    m.d.comb += [
                        r.eq(self.inputa | self.inputb),
                    ]
                    with m.If(~Initial()):
                        m.d.comb += [
                            Assert(self.result == r),
                            Assert(self._psw.N == r[7]),
                            Assert(self._psw.V == self.PSW.V),
                            Assert(self._psw.P == self.PSW.P),
                            Assert(self._psw.B == self.PSW.B),
                            Assert(self._psw.H == self.PSW.H),
                            Assert(self._psw.I == self.PSW.I),
                            Assert(self._psw.Z == ~(r.bool())),
                            Assert(self._psw.C == self.PSW.C),
                        ]

            with m.Case(Operation.EOR):
                m.d.comb += [
                    self.result.eq(self.inputa ^ self.inputb),
                    self._psw.N.eq(self.result.as_signed() < 0),
                    self._psw.Z.eq(self.result == 0),
                ]
                if self.verification is Operation.EOR:
                    r = Signal(8)
                    m.d.comb += [
                        r.eq(self.inputa ^ self.inputb),
                    ]
                    with m.If(~Initial()):
                        m.d.comb += [
                            Assert(self.result == r),
                            Assert(self._psw.N == r[7]),
                            Assert(self._psw.V == self.PSW.V),
                            Assert(self._psw.P == self.PSW.P),
                            Assert(self._psw.B == self.PSW.B),
                            Assert(self._psw.H == self.PSW.H),
                            Assert(self._psw.I == self.PSW.I),
                            Assert(self._psw.Z == ~(r.bool())),
                            Assert(self._psw.C == self.PSW.C),
                        ]

            with m.Case(Operation.INC):
                m.d.comb += [
                    self.result.eq(self.inputa + 1),
                    self._psw.N.eq(self.result.as_signed() < 0),
                    self._psw.Z.eq(self.result == 0),
                ]
                if self.verification is Operation.INC:
                    r = Signal(8)
                    m.d.comb += [
                        r.eq(self.inputa + 1),
                    ]
                    with m.If(~Initial()):
                        m.d.comb += [
                            Assert(self.result == r),
                            Assert(self._psw.N == r[7]),
                            Assert(self._psw.V == self.PSW.V),
                            Assert(self._psw.P == self.PSW.P),
                            Assert(self._psw.B == self.PSW.B),
                            Assert(self._psw.H == self.PSW.H),
                            Assert(self._psw.I == self.PSW.I),
                            Assert(self._psw.Z == ~(r.bool())),
                            Assert(self._psw.C == self.PSW.C),
                        ]

            with m.Case(Operation.DEC):
                m.d.comb += [
                    self.result.eq(self.inputa - 1),
                    self._psw.N.eq(self.result.as_signed() < 0),
                    self._psw.Z.eq(self.result == 0),
                ]
                if self.verification is Operation.DEC:
                    r = Signal(8)
                    m.d.comb += [
                        r.eq(self.inputa - 1),
                    ]
                    with m.If(~Initial()):
                        m.d.comb += [
                            Assert(self.result == r),
                            Assert(self._psw.N == r[7]),
                            Assert(self._psw.V == self.PSW.V),
                            Assert(self._psw.P == self.PSW.P),
                            Assert(self._psw.B == self.PSW.B),
                            Assert(self._psw.H == self.PSW.H),
                            Assert(self._psw.I == self.PSW.I),
                            Assert(self._psw.Z == ~(r.bool())),
                            Assert(self._psw.C == self.PSW.C),
                        ]

            with m.Case(Operation.ASL):
                m.d.comb += [
                    Cat(self.result, self._psw.C).eq(Cat(Const(0), self.inputa)),
                    self._psw.N.eq(self.result.as_signed() < 0),
                    self._psw.Z.eq(self.result == 0),
                ]
                if self.verification is Operation.ASL:
                    r = Signal(8)
                    m.d.comb += [
                        r.eq(self.inputa * 2),
                    ]
                    with m.If(~Initial()):
                        m.d.comb += [
                            Assert(self.result == r),
                            Assert(self._psw.N == self.inputa[6]),
                            Assert(self._psw.V == self.PSW.V),
                            Assert(self._psw.P == self.PSW.P),
                            Assert(self._psw.B == self.PSW.B),
                            Assert(self._psw.H == self.PSW.H),
                            Assert(self._psw.I == self.PSW.I),
                            Assert(self._psw.Z == ~(r.bool())),
                            Assert(self._psw.C == self.inputa[7]),
                        ]

            with m.Case(Operation.LSR):
                m.d.comb += [
                    Cat(self._psw.C, self.result).eq(Cat(self.inputa, Const(0))),
                    self._psw.N.eq(self.result.as_signed() < 0),
                    self._psw.Z.eq(self.result == 0),
                ]
                if self.verification is Operation.LSR:
                    r = Signal(8)
                    m.d.comb += [
                        r.eq(self.inputa // 2),
                    ]
                    with m.If(~Initial()):
                        m.d.comb += [
                            Assert(self.result == r),
                            Assert(self._psw.N == 0),
                            Assert(self._psw.V == self.PSW.V),
                            Assert(self._psw.P == self.PSW.P),
                            Assert(self._psw.B == self.PSW.B),
                            Assert(self._psw.H == self.PSW.H),
                            Assert(self._psw.I == self.PSW.I),
                            Assert(self._psw.Z == ~(r.bool())),
                            Assert(self._psw.C == self.inputa[0]),
                        ]

            with m.Case(Operation.ROL):
                m.d.comb += [
                    Cat(self.result, self._psw.C).eq(Cat(self.PSW.C, self.inputa)),
                    self._psw.N.eq(self.result.as_signed() < 0),
                    self._psw.Z.eq(self.result == 0),
                ]
                if self.verification is Operation.ROL:
                    r = Signal(8)
                    m.d.comb += [
                        r.eq(self.inputa * 2 + self.PSW.C),
                    ]
                    with m.If(~Initial()):
                        m.d.comb += [
                            Assert(self.result == r),
                            Assert(self._psw.N == self.inputa[6]),
                            Assert(self._psw.V == self.PSW.V),
                            Assert(self._psw.P == self.PSW.P),
                            Assert(self._psw.B == self.PSW.B),
                            Assert(self._psw.H == self.PSW.H),
                            Assert(self._psw.I == self.PSW.I),
                            Assert(self._psw.Z == ~(r.bool())),
                            Assert(self._psw.C == self.inputa[7]),
                        ]

            with m.Case(Operation.ROR):
                m.d.comb += [
                    Cat(self._psw.C, self.result).eq(Cat(self.inputa, self.PSW.C)),
                    self._psw.N.eq(self.result.as_signed() < 0),
                    self._psw.Z.eq(self.result == 0),
                ]
                if self.verification is Operation.ROR:
                    r = Signal(8)
                    m.d.comb += [
                        r.eq(self.inputa // 2 + Cat(Signal(7), self.PSW.C)),
                    ]
                    with m.If(~Initial()):
                        m.d.comb += [
                            Assert(self.result == r),
                            Assert(self._psw.N == self.PSW.C),
                            Assert(self._psw.V == self.PSW.V),
                            Assert(self._psw.P == self.PSW.P),
                            Assert(self._psw.B == self.PSW.B),
                            Assert(self._psw.H == self.PSW.H),
                            Assert(self._psw.I == self.PSW.I),
                            Assert(self._psw.Z == ~(r.bool())),
                            Assert(self._psw.C == self.inputa[0]),
                        ]

            with m.Case(Operation.XCN):
                m.d.comb += [
                    self.result.eq(Cat(self.inputa[4:], self.inputa[:4])),
                    self._psw.N.eq(self.result.as_signed() < 0),
                    self._psw.Z.eq(self.result == 0),
                ]
                if self.verification is Operation.XCN:
                    r = Signal(8)
                    m.d.comb += [
                        r.eq(self.inputa * 16 + self.inputa // 16),
                    ]
                    with m.If(~Initial()):
                        m.d.comb += [
                            Assert(self.result == r),
                            Assert(self._psw.N == self.inputa[3]),
                            Assert(self._psw.V == self.PSW.V),
                            Assert(self._psw.P == self.PSW.P),
                            Assert(self._psw.B == self.PSW.B),
                            Assert(self._psw.H == self.PSW.H),
                            Assert(self._psw.I == self.PSW.I),
                            Assert(self._psw.Z == ~(self.inputa.bool())),
                            Assert(self._psw.C == self.PSW.C),
                        ]

            with m.Case(Operation.DAA):
                temp = Signal().like(self.inputa)
                with m.If(self.PSW.C | (self.inputa > 0x99)):
                    m.d.comb += self._psw.C.eq(1)
                    m.d.comb += temp.eq(self.inputa + 0x60)
                with m.Else():
                    m.d.comb += temp.eq(self.inputa)

                with m.If(self.PSW.H | (temp[:4] > 0x09)):
                    m.d.comb += self.result.eq(temp + 0x06)

                m.d.comb += [
                    self._psw.N.eq(self.result & 0x80),
                    self._psw.Z.eq(self.result == 0),
                ]
                if self.verification is Operation.DAA:
                    with m.If(~Initial()):
                        m.d.comb += [Assert(False)]

            with m.Case(Operation.DAS):
                temp = Signal().like(self.inputa)
                with m.If(~self.PSW.C | (self.inputa > 0x99)):
                    m.d.comb += self._psw.C.eq(0)
                    m.d.comb += temp.eq(self.inputa - 0x60)
                with m.Else():
                    m.d.comb += temp.eq(self.inputa)

                with m.If(~self.PSW.H | (temp[:4] > 0x09)):
                    m.d.comb += self.result.eq(temp - 0x06)

                m.d.comb += [
                    self._psw.N.eq(self.result & 0x80),
                    self._psw.Z.eq(self.result == 0),
                ]
                if self.verification is Operation.DAS:
                    with m.If(~Initial()):
                        m.d.comb += [Assert(False)]

        return m


class ALU(Elaboratable):
    def __init__(self, verification: Operation = None):
        self.inputa = Signal(8)
        self.inputb = Signal(8)
        self.result = Signal(8)
        self.oper = Signal(Operation)

        self.PSW = Status()

        self.verification = verification

    def ports(self) -> List[Signal]:
        return [self.inputa, self.inputb, self.oper, self.result]

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        m.submodules.big = big = ALU_big(self.verification)

        m.d.comb += [
            big.inputa.eq(Cat(self.inputa[:4], self.inputa[4:])),
            big.inputb.eq(Cat(self.inputb[:4], self.inputb[4:])),
            big.oper.eq(self.oper),
            self.result.eq(Cat(big.result[:4], big.result[4:])),
            self.PSW.eq(big.PSW),
        ]

        return m


if __name__ == "__main__":
    parser = main_parser()
    parser.add_argument("--oper")
    args = parser.parse_args()

    oper: Optional[Operation] = None
    if args.oper is not None:
        oper = Operation[args.oper]

    m = Module()
    m.submodules.alu = alu = ALU_big(oper)

    if oper is not None:
        m.d.comb += Assume(~ResetSignal())
        m.d.comb += Assume(alu.oper == oper)
        main_runner(parser, args, m, ports=alu.ports())

    else:
        sim = Simulator(m)

        def process():
            yield
            yield alu.inputa.eq(0x12)
            yield alu.inputb.eq(0x34)
            yield alu.oper.eq(Operation.ADC)
            yield
            yield
            yield alu.inputa.eq(0x7F)
            yield alu.inputb.eq(0x7F)
            yield alu.oper.eq(Operation.ADC)
            yield
            yield

        sim.add_clock(1e-6)  # 1 MHz
        sim.add_sync_process(process)
        with sim.write_vcd("test.vcd", "test.gtkw", traces=alu.ports()):
            sim.run()
