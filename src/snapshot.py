# snapshot.py: Snapshot the current cpu state to perform formal verification
# Copyright (C) 2021 Martín Bárez <martinbarez>

# verification.py: Formal verification framework for the 6800 CPU.
# Copyright (C) 2019 Robert Baruch <robert.c.baruch@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from nmigen import Array, Module, Signal, Value

from registers import Registers


class Snapshot:
    def __init__(self):
        self.taken = Signal(reset=0)

        self.pre = Registers()
        self.post = Registers()

        self.addresses_written = Signal(3, reset=0)
        self.write_addr = Array([Signal(16) for _ in range(8)])
        self.write_data = Array([Signal(8) for _ in range(8)])

        self.addresses_read = Signal(3, reset=0)
        self.read_addr = Array([Signal(16) for _ in range(8)])
        self.read_data = Array([Signal(8) for _ in range(8)])

    def add16(self, v1: Value, v2: Value) -> Value:
        return (v1 + v2)[:16]

    def add8(self, v1: Value, v2: Value) -> Value:
        return (v1 + v2)[:8]

    def read(self, m: Module, addr: Value, data: Value):
        with m.If(self.addresses_read != 7):
            m.d.sync += self.addresses_read.eq(self.addresses_read + 1)
            m.d.sync += self.read_addr[self.addresses_read].eq(addr)
            m.d.sync += self.read_data[self.addresses_read].eq(data)

    def write(self, m: Module, addr: Value, data: Value):
        with m.If(self.addresses_written != 7):
            m.d.sync += self.addresses_written.eq(self.addresses_written + 1)
            m.d.sync += self.write_addr[self.addresses_written].eq(addr)
            m.d.sync += self.write_data[self.addresses_written].eq(data)

    def pre_snapshot(self, m: Module, addr: Value, data: Value, reg: Registers):
        """take a synchronous snapshot including addr and data read from ram"""
        m.d.sync += [
            self.taken.eq(1),
            self.pre.eq(reg),
            self.read_addr[0].eq(addr),
            self.read_data[0].eq(data),
            self.addresses_read.eq(1),
            self.addresses_written.eq(0),
        ]

    def no_snapshot(self, m: Module):
        m.d.sync += self.taken.eq(0)

    def post_snapshot(self, m: Module, reg: Registers):
        m.d.comb += self.post.eq(reg)
