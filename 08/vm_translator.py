import sys, os

# Initializing label counter for generating unique labels in comparison operations and a way to track current function.
label_counter = 0
current_function = "Sys.init"


# Generates a bootstrap code.
def write_bootstrap():
    return ["@256", "D=A", "@SP", "M=D"] + functions(["call", "Sys.init", "0"])


# Handles push and pop commands for different memory segments.
def push_pop(parts, filename):
    command, segment, index = parts
    index = int(index)

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


# Handles branching operations
def branching(parts):
    global current_function
    label = f"{current_function}${parts[1]}"

    if parts[0] == "label":
        return [f"({label})"]

    elif parts[0] == "goto":
        return [f"@{label}", "0;JMP"]

    elif parts[0] == "if-goto":
        return ["@SP", "M=M-1", "A=M", "D=M", f"@{label}", "D;JNE"]


# Handles functions, function calls and returns
def functions(parts):
    global current_function
    global label_counter
    ret = []

    if parts[0] == "function":
        current_function = parts[1]
        ret += [f"({current_function})"]
        for _ in range(int(parts[2])):
            ret += ["@SP", "A=M", "M=0", "@SP", "M=M+1"]

    elif parts[0] == "call":
        return_label = f"{current_function}$ret.{label_counter}"
        label_counter += 1

        ret += [
            f"@{return_label}",
            "D=A",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
            "@LCL",
            "D=M",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
            "@ARG",
            "D=M",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
            "@THIS",
            "D=M",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
            "@THAT",
            "D=M",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
            f"@{int(parts[2]) + 5}",
            "D=A",
            "@SP",
            "D=M-D",
            "@ARG",
            "M=D",
            "@SP",
            "D=M",
            "@LCL",
            "M=D",
            f"@{parts[1]}",
            "0;JMP",
            f"({return_label})",
        ]

    elif parts[0] == "return":
        ret += [
            "@LCL",
            "D=M",
            "@R13",
            "M=D",
            "@5",
            "D=A",
            "@R13",
            "A=M-D",
            "D=M",
            "@R14",
            "M=D",
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            "@ARG",
            "A=M",
            "M=D",
            "@ARG",
            "D=M+1",
            "@SP",
            "M=D",
            "@R13",
            "A=M-1",
            "D=M",
            "@THAT",
            "M=D",
            "@2",
            "D=A",
            "@R13",
            "A=M-D",
            "D=M",
            "@THIS",
            "M=D",
            "@3",
            "D=A",
            "@R13",
            "A=M-D",
            "D=M",
            "@ARG",
            "M=D",
            "@4",
            "D=A",
            "@R13",
            "A=M-D",
            "D=M",
            "@LCL",
            "M=D",
            "@R14",
            "A=M",
            "0;JMP",
        ]

    return ret


# Reads a .vm file, translates it into Hack assembly, and writes to a .asm file.
def translate(input_path):
    assembly_code = []

    if os.path.isdir(input_path):
        output_file = os.path.join(input_path, os.path.basename(input_path) + ".asm")
        vm_files = [
            os.path.join(input_path, f)
            for f in os.listdir(input_path)
            if f.endswith(".vm")
        ]
    else:
        output_file = input_path.replace(".vm", ".asm")
        vm_files = [input_path]

    if len(vm_files) > 1 or "Sys.vm" in [os.path.basename(f) for f in vm_files]:
        assembly_code.extend(write_bootstrap())

    for vm_file in vm_files:
        stripped_filename = os.path.basename(vm_file).replace(".vm", "")
        with open(vm_file, "r") as f:
            lines = f.readlines()

        for line in lines:
            line = line.split("//")[0].strip()
            if line:
                parts = line.split()
                if parts[0] in ["push", "pop"] and parts[2].isdigit():
                    assembly_code.extend(push_pop(parts, stripped_filename))
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
                elif parts[0] in ["label", "goto", "if-goto"]:
                    assembly_code.extend(branching(parts))
                elif parts[0] in ["function", "call", "return"]:
                    assembly_code.extend(functions(parts))
                else:
                    print(f"Error: Unrecognized command '{line}' in {vm_file}")

    with open(output_file, "w") as f:
        f.write("\n".join(assembly_code))

    print(f"Translated VM file to {output_file}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 vm_translator.py <filename.vm> or <directory>")
        sys.exit(1)

    translate(sys.argv[1])
