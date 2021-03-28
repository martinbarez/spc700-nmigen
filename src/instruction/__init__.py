# instruction.__init__.py: Instruction class definition
# Copyright (C) 2021 Martín Bárez <martinbarez>

from abc import ABC, abstractmethod

from nmigen import Module, Value

from snapshot import Snapshot


class Instruction(ABC):
    @staticmethod
    @abstractmethod
    def synth(m: Module, instr: Value):
        pass

    @staticmethod
    @abstractmethod
    def check(m: Module, instr: Value, snapshot: Snapshot):
        pass
