import sys

# Initializing label counter for generating unique labels in comparison operations.
label_counter = 0


# Handles push and pop commands for different memory segments.
def push_pop(parts, filename):
    command, segment, index = parts
    index = int(index)

    # Extract filename without path
    if "/" in filename:
        filename = filename.split("/")[-1]
    elif "\\" in filename:
        filename = filename.split("\\")[-1]

    # Mapping VM segments to assembly equivalents.
    segment_map = {
        "local": "LCL",
        "argument": "ARG",
        "this": "THIS",
        "that": "THAT",
        "temp": "R5",
        "pointer": "R3",
        "static": "16",
    }

    ret = []

    # Pushing values onto the stack.
    if command == "push":
        if segment == "constant":
            ret = [f"@{index}", "D=A"]
        elif segment in ["local", "argument", "this", "that"]:
            ret = [f"@{segment_map[segment]}", "D=M", f"@{index}", "A=D+A", "D=M"]
        elif segment in ["temp", "pointer"]:
            ret = [f"@{segment_map[segment]}", "D=A", f"@{index}", "A=D+A", "D=M"]
        elif segment == "static":
            ret = [f"@{filename}.{index}", "D=M"]
        ret += ["@SP", "A=M", "M=D", "@SP", "M=M+1"]

    # Popping values from the stack.
    elif command == "pop":
        if segment in ["local", "argument", "this", "that"]:
            ret = [
                f"@{segment_map[segment]}",
                "D=M",
                f"@{index}",
                "D=D+A",
                "@R13",
                "M=D",
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                "@R13",
                "A=M",
                "M=D",
            ]
        elif segment in ["temp", "pointer"]:
            ret = [
                f"@{segment_map[segment]}",
                "D=A",
                f"@{index}",
                "D=D+A",
                "@R13",
                "M=D",
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                "@R13",
                "A=M",
                "M=D",
            ]
        elif segment == "static":
            ret = ["@SP", "M=M-1", "A=M", "D=M", f"@{filename}.{index}", "M=D"]

    return ret


# Handles arithmetic and logical operations.
def arithmetic_logic(operation):
    global label_counter
    ret = []

    if operation in ["add", "sub", "or", "and"]:
        ret = ["@SP", "M=M-1", "A=M", "D=M", "@SP", "M=M-1", "A=M"]
        if operation == "add":
            ret += ["M=D+M"]
        elif operation == "sub":
            ret += ["M=M-D"]
        elif operation == "and":
            ret += ["M=D&M"]
        elif operation == "or":
            ret += ["M=D|M"]
        ret += ["@SP", "M=M+1"]

    elif operation in ["neg", "not"]:
        ret = ["@SP", "M=M-1", "A=M"]
        if operation == "neg":
            ret += ["M=-M"]
        elif operation == "not":
            ret += ["M=!M"]
        ret += ["@SP", "M=M+1"]

    elif operation in ["eq", "gt", "lt"]:
        ret = [
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            "@SP",
            "M=M-1",
            "A=M",
            "D=M-D",
            f"@TRUE_{label_counter}",
        ]
        if operation == "eq":
            ret += ["D;JEQ"]
        elif operation == "gt":
            ret += ["D;JGT"]
        elif operation == "lt":
            ret += ["D;JLT"]

        ret += [
            "@SP",
            "A=M",
            "M=0",
            f"@END_{label_counter}",
            "0;JMP",
            f"(TRUE_{label_counter})",
            "@SP",
            "A=M",
            "M=-1",
            f"(END_{label_counter})",
            "@SP",
            "M=M+1",
        ]

        label_counter += 1

    return ret


# Reads a .vm file, translates it into Hack assembly, and writes to a .asm file.
def translate(filename):
    output_file = filename.replace(".vm", ".asm")
    assembly_code = []

    with open(filename, "r") as f:
        lines = f.readlines()

    for line in lines:
        # Remove comments and strip whitespace.
        line = line.split("//")[0].strip()
        if line:
            parts = line.split()
            if (
                parts[0] in ["push", "pop"]
                and parts[1]
                in [
                    "constant",
                    "local",
                    "argument",
                    "this",
                    "that",
                    "temp",
                    "pointer",
                    "static",
                ]
                and parts[2].isdigit()
            ):
                assembly_code.extend(push_pop(parts, filename))
            elif parts[0] in [
                "add",
                "sub",
                "neg",
                "eq",
                "gt",
                "lt",
                "and",
                "or",
                "not",
            ]:
                assembly_code.extend(arithmetic_logic(parts[0]))
            else:
                print(f"Error: Unrecognized command '{line}' in {filename}")

    with open(output_file, "w") as f:
        f.write("\n".join(assembly_code))

    print(f"Translated VM file to {output_file}")


if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".vm"):
        print("Usage: python3 vm_translator.py <filename.vm>")
        sys.exit(1)
    translate(sys.argv[1])
