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
@addr //Addr iterates over the screen addresses.
M = D
@KBD
D = M
@SETBLACK //If keyboard key not 0, set black
D;JNE
@SETWHITE //Else set white
0;JMP
(FILL)
@addr
D = M
//If addr is >= than KBD(screen end) then fill is done, restart.
@KBD
D = D - A
@START
D;JGE
@color //Store color on D.
D = M
@addr //Move address register to addr pointer.
A = M
M = D //Set the screen portion to saved color.
@addr
M = M + 1 //Increment the screen address by 1.
@FILL //Keep filling.
0;JMP
(SETBLACK)
@color
M = -1
@FILL
0;JMP
(SETWHITE)
@color
M = 0
@FILL
0;JMP
