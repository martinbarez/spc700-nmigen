# registers.py: Registers of the SPC-700 CPU
# Copyright (C) 2021 Martín Bárez <martinbarez>

from __future__ import annotations

from nmigen import Cat, Signal, Value


class Status:
    def __init__(self):
        self.N = Signal()  # Negative
        self.V = Signal()  # oVerflow
        self.P = Signal()  # direct Page
        self.B = Signal()  # Break
        self.H = Signal()  # Half carry
        self.I = Signal()  # Interrupt enabled (unused)
        self.Z = Signal()  # Zero
        self.C = Signal()  # Carry

    def __eq__(self, other: Status):
        return (
            (self.N == other.N)
            & (self.V == other.V)
            & (self.P == other.P)
            & (self.B == other.B)
            & (self.H == other.H)
            & (self.I == other.I)
            & (self.Z == other.Z)
            & (self.C == other.C)
        )

    def eq(self, other: Status):
        return [
            self.N.eq(other.N),
            self.V.eq(other.V),
            self.P.eq(other.P),
            self.B.eq(other.B),
            self.H.eq(other.H),
            self.I.eq(other.I),
            self.Z.eq(other.Z),
            self.C.eq(other.C),
        ]


class Registers:
    def __init__(self):
        self.A = Signal(8)
        self.X = Signal(8)
        self.Y = Signal(8)
        self.SP = Signal(8)
        self.PC = Signal(16)
        self.PSW = Status()

    def __eq__(self, other: Registers):
        return (
            (self.A == other.A)
            & (self.X == other.X)
            & (self.Y == other.Y)
            & (self.SP == other.SP)
            & (self.PC == other.PC)
            & (self.PSW == other.PSW)
        )

    def eq(self, other: Registers):
        return [
            self.A.eq(other.A),
            self.X.eq(other.X),
            self.Y.eq(other.Y),
            self.SP.eq(other.SP),
            self.PC.eq(other.PC),
            self.PSW.eq(other.PSW),
        ]


def add8(value: Value, incr) -> Value:
    """Add incr to a 8 bit value in little endiann"""
    if type(incr) is not int:
        raise TypeError
    t = Cat(value[4:8], value[0:4]) + incr
    return Cat(t[4:8], t[0:4])


def add16(value: Value, incr: int) -> Value:
    """Add incr to a 16 bit value in little endiann"""
    if type(incr) is not int:
        raise TypeError
    t = Cat(value[12:16], value[8:12], value[4:8], value[0:4]) + incr
    return Cat(t[12:16], t[8:12], t[4:8], t[0:4])
