// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

(LISTEN_KBD)
            // Check if any key is pressed.
            @KBD
            D=M
            // Set the color to black.
            @color
            M=-1
            // Fill the screen with black if any key is pressed.
            @SET_POINTER
            D;JNE
            // If no key is pressed, set the color to white.
            @color
            M=0
(SET_POINTER)
            // Set screen pointer.
            @SCREEN
            D=A
            @pointer
            M=D
(NOT_FILL)
            // Check if fill is even needed.
            // If the last pixel is desired color, then the filling process is skipped.
            // This might help with performance.
            @24575
            D=M
            @color
            D=D-M
            @LISTEN_KBD
            D;JEQ
(FILL)
            // Start filling.
            @color
            D=M
            @pointer
            A=M
            M=D
            // Increment screen pointer.
            @pointer
            M=M+1
            D=M
            // If screen is filled, repeat.
            @24576
            D=A-D
            @LISTEN_KBD
            D;JEQ
            // Else, keep filling.
            @FILL
            0;JMP
            