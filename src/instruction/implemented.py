# implemented.py: A list with all implemented instructions
# Copyright (C) 2021 Martín Bárez <martinbarez>

from . import absolute, implied

# !abs
_absolute = [
    absolute.MOV_A_read,  # E5
    # absolute.MOV_x_read,  # E9
    # absolute.MOV_Y_read,  # EC
    absolute.MOV_A_write,  # C5
    # absolute.MOV_X_write,  # C9
    # absolute.MOV_Y_write,  # CC
    absolute.ADC,  # 85
    # absolute.SBC,  # A5
    # absolute.CMP_A,  # 65
    # absolute.CMP_X,  # 1E
    # absolute.CMP_Y,  # 5E
    # absolute.AND,  # 25
    # absolute.OR,  # 05
    # absolute.EOR,  # 45
    # absolute.INC,  # AC
    # absolute.DEC,  # 8C
    # absolute.ASL,  # 0C
    # absolute.LSR,  # 4C
    # absolute.ROL,  # 2C
    # absolute.ROR,  # 6C
    absolute.JMP,  # 5F
    # absolute.CALL,  # 3F
    # absolute.TSET1,  # 0E
    # absolute.TCLR1,  # 4E
]

# [!abs+X]
_absolute_indexed_indirect = [
    # JMP,  # 1F
]

# !abs+-
_absolute_XY = [
    # MOV,  # F5
    # MOV,  # D5
    # ADC,  # 95
    # SBC,  # B5
    # CMP,  # 75
    # AND,  # 35
    # OR ,  # 15
    # EOR,  # 55
    # MOV,  # F6
    # MOV,  # D6
    # ADC,  # 96
    # SBC,  # B6
    # CMP,  # 76
    # AND,  # 36
    # OR ,  # 16
    # EOR,  # 56
]

# -, dp
_direct_dp = [
    # MOV,  # E4
    # MOV,  # F8
    # MOV,  # EB
    # MOV,  # C4
    # MOV,  # D8
    # MOV,  # CB
    # ADC,  # 84
    # SBC,  # A4
    # CMP,  # 64
    # CMP,  # 3E
    # CMP,  # 7E
    # AND,  # 24
    # OR ,  # 04
    # EOR,  # 44
    # INC,  # AB
    # DEC,  # 8B
    # ASL,  # 0B
    # LSR,  # 4B
    # ROL,  # 2B
    # ROR,  # 6B
    # MOVW,  # BA
    # MOVW,  # DA
    # INCW,  # 3A
    # DECW,  # 1A
    # ADDW,  # 7A
    # SUBW,  # 9A
    # CMPW,  # 5A
    # SET1,  # x2
    # CLR1,  # y2
]

# dp, dp
_dp_dp = [
    # MOV,  # FA
    # ADC,  # 89
    # SBC,  # A9
    # CMP,  # 69
    # AND,  # 29
    # OR ,  # 09
    # EOR,  # 49
]

# dp, #imm
_direct_immediate = [
    # MOV,  # 8F
    # ADC,  # 98
    # SBC,  # B8
    # CMP,  # 78
    # AND,  # 38
    # OR ,  # 18
    # EOR,  # 58
]

# -, [dp+-]
_indirect_dp = [
    # MOV,  # E7
    # MOV,  # C7
    # ADC,  # 87
    # SBC,  # A7
    # CMP,  # 67
    # AND,  # 27
    # OR ,  # 07
    # EOR,  # 47
    # MOV,  # F7
    # MOV,  # D7
    # ADC,  # 97
    # SBC,  # B7
    # CMP,  # 77
    # AND,  # 37
    # OR ,  # 17
    # EOR,  # 57
]

# dp, rel
_direct_relative = [
    # BBS ,  # x3
    # BBC ,  # y3
    # CBNE,  # 2E
    # DBNZ,  # 6E
]

# -, dp+-
_direct_XY = [
    # MOV,  # F4
    # MOV,  # D4
    # ADC,  # 94
    # SBC,  # B4
    # CMP,  # 74
    # AND,  # 34
    # OR ,  # 14
    # EOR,  # 54
    # INC,  # BB
    # DEC,  # 9B
    # ASL,  # 1B
    # LSR,  # 5B
    # ROL,  # 3B
    # ROR,  # 7B
    # MOV,  # F9
    # MOV,  # D9
    # MOV,  # FB
    # MOV,  # DB
]

# -, (-)
_indirect = [
    # MOV,  # E6
    # MOV,  # C6
    # ADC,  # 86
    # SBC,  # A6
    # CMP,  # 66
    # AND,  # 26
    # OR ,  # 06
    # EOR,  # 46
    # MOV,  # BF
    # MOV,  # AF
]

# (X), (Y)
_indirect_indirect = [
    # ADC,  # 99
    # SBC,  # B9
    # CMP,  # 79
    # AND,  # 39
    # OR ,  # 19
    # EOR,  # 59
]

# -, #imm
_immediate = [
    # MOV,  # E8
    # MOV,  # CD
    # MOV,  # 8D
    # ADC,  # 88
    # SBC,  # A8
    # CMP,  # 68
    # CMP,  # C8
    # CMP,  # AD
    # AND,  # 28
    # OR ,  # 08
    # EOR,  # 48
]

# 1 byte, direct
_implied = [
    # implied.MOV_A_X,  # 7D
    # implied.MOV_A_Y,  # DD
    # implied.MOV_X_A,  # 5D
    # implied.MOV_Y_A,  # FD
    # implied.MOV_X_SP,  # 9D
    # implied.MOV_SP_X,  # BD
    # INC,  # BC
    # INC,  # 3D
    # INC,  # FC
    # DEC,  # 9C
    # DEC,  # 1D
    # DEC,  # DC
    # ASL,  # 1C
    # LSR,  # 5C
    # ROL,  # 3C
    # ROR,  # 7C
    # implied.XCN,  # 9F
    implied.MUL,  # CF
    # implied.DIV,  # 9E
    # implied.DAA,  # DF
    # implied.DAS,  # BE
    # implied.CLRC,  # 60
    # implied.SETC,  # 80
    # implied.NOTC,  # ED
    # implied.CLRV,  # E0
    # implied.CLRP,  # 20
    # implied.SETP,  # 40
    # implied.EI,  # A0
    # implied.DI,  # C0
    # implied.NOP,  # 00
    # SLEEP,  # EF
    # STOP,  # FF
]

# bit manipulation
_bit = [
    # AND1,  # 4A
    # AND1,  # 6A
    # OR1 ,  # 0A
    # OR1 ,  # 2A
    # EOR1,  # 8A
    # NOT1,  # EA
    # MOV1,  # AA
    # MOV1,  # CA
]

# rel
_relative = [
    # BRA,  # 2F
    # BEQ,  # F0
    # BNE,  # D0
    # BCS,  # B0
    # BCC,  # 90
    # BVS,  # 70
    # BVC,  # 50
    # BMI,  # 30
    # BPL,  # 10
    # DBNZ,  # FE
]

# stack operations
_stack = [
    # PCALL,  # 4F
    # TCALL,  # n1
    # BRK,  # 0F
    # RET,  # 6F
    # RETI,  # 7F
    # PUSH,  # 2D
    # PUSH,  # 4D
    # PUSH,  # 6D
    # PUSH,  # 0D
    # POP,  # AE
    # POP,  # CE
    # POP,  # EE
    # POP,  # 8E
]


implemented = (
    _absolute
    + _absolute_indexed_indirect
    + _absolute_XY
    + _direct_dp
    + _dp_dp
    + _direct_immediate
    + _indirect_dp
    + _direct_relative
    + _direct_XY
    + _indirect
    + _indirect_indirect
    + _immediate
    + _implied
    + _bit
    + _relative
    + _stack
)

for i in implemented:
    i()
