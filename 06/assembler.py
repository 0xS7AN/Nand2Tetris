import sys

COMP_TABLE = {
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "!D": "0001101",
    "!A": "0110001",
    "-D": "0001111",
    "-A": "0110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "D+A": "0000010",
    "D-A": "0010011",
    "A-D": "0000111",
    "D&A": "0000000",
    "D|A": "0010101",
    "M": "1110000",
    "!M": "1110001",
    "M+1": "1110111",
    "M-1": "1110010",
    "D+M": "1000010",
    "D-M": "1010011",
    "M-D": "1000111",
    "D&M": "1000000",
    "D|M": "1010101",
}

DEST_TABLE = {
    "null": "000",
    "M": "001",
    "D": "010",
    "MD": "011",
    "A": "100",
    "AM": "101",
    "AD": "110",
    "AMD": "111",
}

JUMP_TABLE = {
    "null": "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111",
}

SYMBOLS = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "SCREEN": 16384,
    "KBD": 24576,
}

for i in range(16):
    label = "R" + str(i)
    SYMBOLS[label] = i


def first_pass(lines):
    rom_address = 0
    filtered_lines = []
    for line in lines:
        if line.startswith("("):
            label = line[1:-1]
            SYMBOLS[label] = rom_address
        else:
            filtered_lines.append(line)
            rom_address += 1
    return filtered_lines


def second_pass(lines):
    var_address = 16
    output = []
    for line in lines:
        if line.startswith("@"):
            variable = line[1:]
            if not variable.isdigit():
                if variable not in SYMBOLS:
                    SYMBOLS[variable] = var_address
                    var_address += 1
                line = f"@{SYMBOLS[variable]}"
        output.append(line)
    return output


def a_instruction(line):
    return f"0{int(line[1:]):015b}"


def c_instruction(line):
    comp, dest, jump = "", "null", "null"
    if "=" in line:
        parts = line.split("=")
        dest, line = parts[0], parts[1]
    if ";" in line:
        parts = line.split(";")
        comp, jump = parts[0], parts[1]
    else:
        comp = line
    return f"111{COMP_TABLE[comp]}{DEST_TABLE[dest]}{JUMP_TABLE[jump]}"


def assemble(filename):
    lines = []
    with open(filename, "r") as f:
        for line in f:
            parts = line.split("//")
            instruction = parts[0].strip()
            if instruction:
                lines.append(instruction)
    lines = first_pass(lines)
    lines = second_pass(lines)
    binary = []
    for line in lines:
        if line.startswith("@"):
            binary.append(a_instruction(line))
        else:
            binary.append(c_instruction(line))
    with open(filename.replace(".asm", ".hack"), "w") as f:
        f.write("\n".join(binary))
    print("Done!!!")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 assembler.py <filename.asm>")
        sys.exit(1)
    assemble(sys.argv[1])
