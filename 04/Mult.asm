// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
// The algorithm is based on repetitive addition.

(BEGIN)
        // Init product to 0.
        @R2
        M=0
(LOOP)
        // Start of the LOOP.
        // Jump to the END if R1 <= 0.
        @R1
        D=M
        @END
        D;JLE
        // Add R0 to the product.
        @R0
        D=M
        @R2
        M=M+D
        // Decrement R1 by 1.
        @R1
        M=M-1
        // LOOP again.
        @LOOP
        0;JMP

(END)
        // Terminate the program.
        @END
        0;JMP