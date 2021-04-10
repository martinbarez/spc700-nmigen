# core.py: SPC-700 CPU core and main runner
# Copyright (C) 2021 Martín Bárez <martinbarez>

from sys import modules
from typing import List, Optional

from nmigen import ClockSignal, Elaboratable, Module, Mux, ResetSignal, Signal
from nmigen.asserts import AnyConst, Assume, Cover, Fell, Initial
from nmigen.build import Platform
from nmigen.cli import main_parser, main_runner
from nmigen.sim import Simulator

from alu import ALU, Operation
from instruction import Instruction, implemented
from registers import Registers, add16
from snapshot import Snapshot


class Core(Elaboratable):
    def __init__(self, verification: Instruction = None):
        self.enable = Signal(reset=1)
        self.addr = Signal(16)
        self.din = Signal(8)
        self.dout = Signal(8)
        self.RWB = Signal(reset=1)  # 1 = read, 0 = write

        # registers
        self.reg = Registers()
        self.tmp = Signal(8)  # temp signal when reading 16 bits

        # internal exec state
        self.opcode = Signal(8)
        self.cycle = Signal(4, reset=1)

        # formal verification
        self.verification = verification
        self.snapshot = Snapshot()

    def ports(self) -> List[Signal]:
        return [self.addr, self.din, self.dout, self.RWB]

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        m.submodules.alu = self.alu = ALU()

        """Fetch the opcode, common for all instr"""
        m.d.sync += self.opcode.eq(Mux(self.cycle == 1, self.dout, self.opcode))

        with m.Switch(Mux(self.cycle == 1, self.dout, self.opcode)):
            for i in implemented.implemented:
                with m.Case(i.opcode):
                    i.synth(self, m)
            with m.Default():
                m.d.comb += core.alu.oper.eq(Operation.NOP)
                m.d.sync += [
                    core.reg.PC.eq(add16(core.reg.PC, 1)),
                    core.enable.eq(1),
                    core.addr.eq(add16(core.reg.PC, 1)),
                    core.RWB.eq(1),
                    core.cycle.eq(1),
                ]

        if self.verification is not None:
            self.verify(m)

            with m.If(Initial()):
                m.d.sync += [
                    self.reg.A.eq(AnyConst(8)),
                    self.reg.X.eq(AnyConst(8)),
                    self.reg.Y.eq(AnyConst(8)),
                    self.reg.SP.eq(AnyConst(16)),
                    self.reg.PC.eq(AnyConst(16)),
                ]
                m.d.sync += [
                    self.reg.PSW.N.eq(AnyConst(1)),
                    self.reg.PSW.V.eq(AnyConst(1)),
                    self.reg.PSW.P.eq(AnyConst(1)),
                    self.reg.PSW.B.eq(AnyConst(1)),
                    self.reg.PSW.H.eq(AnyConst(1)),
                    self.reg.PSW.I.eq(AnyConst(1)),
                    self.reg.PSW.Z.eq(AnyConst(1)),
                    self.reg.PSW.C.eq(AnyConst(1)),
                ]

        return m

    def verify(self, m: Module):
        """Take snapshots of the state and check formally"""
        with m.If(self.cycle == 1):
            with m.If(self.dout.matches(self.verification.opcode)):
                self.snapshot.pre_snapshot(m, self.addr, self.dout, self.reg)
            with m.Else():
                self.snapshot.no_snapshot(m)
        with m.Else():
            with m.If(self.snapshot.taken & self.enable):
                """we keep track of every address during instr exec"""
                with m.If(self.RWB == 1):
                    self.snapshot.read(m, self.addr, self.dout)
                with m.If(self.RWB == 0):
                    self.snapshot.write(m, self.addr, self.din)

        with m.If((self.snapshot.taken) & (self.cycle == 1)):
            """at the start of the next instr, check"""
            self.snapshot.post_snapshot(m, self.reg)
            self.verification.check(m, self.snapshot, self.alu)


if __name__ == "__main__":
    parser = main_parser()
    parser.add_argument("--instr")
    args = parser.parse_args()

    instr: Optional[Instruction] = None
    if args.instr is not None:
        instr = getattr(modules["instruction.implemented"], args.instr.split(".")[0])
        instr = getattr(instr, args.instr.split(".")[1])
        if instr not in implemented.implemented:
            raise AttributeError()

    m = Module()
    m.submodules.core = core = Core(instr)

    if instr is not None:
        time = Signal(6, reset_less=True)
        m.d.sync += time.eq(time + 1)

        with m.If(Initial()):
            m.d.sync += Assume(ResetSignal())
        with m.Else():
            m.d.sync += Assume(~ResetSignal())

        # A time slot delayed because PC and addr need to sync
        with m.If(time == 2):
            m.d.sync += Assume(~core.snapshot.taken)
        with m.If(time == 3):
            m.d.sync += Cover(core.snapshot.taken)
            m.d.sync += Assume(core.snapshot.taken)
        m.d.sync += Cover(Fell(core.snapshot.taken))

        main_runner(
            parser, args, m, ports=core.ports() + [ClockSignal(), ResetSignal()]
        )

    else:
        # Fake memory
        mem = {
            0x0000: 0x5F,
            0x1000: 0x12,
            0x2000: 0x34,
            0x1234: 0x5F,
            0x1334: 0x00,
            0x1434: 0x00,
        }
        with m.Switch(core.addr):
            for addr, data in mem.items():
                with m.Case(addr):
                    m.d.comb += core.dout.eq(data)
            with m.Default():
                m.d.comb += core.dout.eq(0xFF)

        sim = Simulator(m)
        sim.add_clock(1e-6, domain="sync")

        def process():
            yield
            yield
            yield
            yield
            yield
            yield
            yield
            yield
            yield
            yield
            yield
            yield
            yield
            yield
            yield
            yield

        sim.add_sync_process(process, domain="sync")
        with sim.write_vcd("test.vcd", "test.gtkw", traces=core.ports()):
            sim.run()
