# implemented.py: A list with all implemented instructions
# Copyright (C) 2021 Martín Bárez <martinbarez>

from . import absolute

_absolute = [
    absolute.MOV_A_read,
    # absolute.MOV_x_read,
    # absolute.MOV_Y_read,
    absolute.MOV_A_write,
    # absolute.MOV_X_write,
    # absolute.MOV_Y_write,
    absolute.ADC,
    # absolute.SBC,
    # absolute.CMP_A,
    # absolute.CMP_X,
    # absolute.CMP_Y,
    # absolute.AND,
    # absolute.OR,
    # absolute.EOR,
    # absolute.CALL,
    absolute.JMP,
    # absolute.INC,
    # absolute.DEC,
    # absolute.ASL,
    # absolute.LSR,
    # absolute.ROL,
    # absolute.ROR,
    # absolute.TSET1,
    # absolute.TCLR1,
]

try:
    assert (
        len(_absolute) == 14 + 1 + 1 + 6 + 2
    ), "Not all absolute instructions are implemented"
except AssertionError:
    pass

implemented = _absolute

for i in implemented:
    i()
