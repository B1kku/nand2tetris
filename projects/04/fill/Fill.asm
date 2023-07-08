// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.
(START)
@SCREEN
D = A
@addr //Addr holds the initial screen's address
M = D
(ITERATE)
@addr
D = M
//If addr is <= than KBD
@KBD
D = D - A
@START
D;JGE
@KBD //If key pressed, set color to black
D = M
@BLACK
D;JNE
@color //Else, white
M = 0
(COLORDONE)
@color
D = M
@addr //Set address to addr value, make that black.
A = M
M = D
@addr
M = M + 1
@ITERATE
0;JMP
(BLACK)
@color
M = -1
@COLORDONE
0;JMP
