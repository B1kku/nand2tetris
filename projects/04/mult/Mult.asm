// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

//Since R1 is the iterator
//if R1 == 0; jump to END
//Else R0 is the value we have to add to the sum.
//R2 is the sum address.
//Reduce R1, repeat.
@R2
M = 0 //Initialize sum to 0
(LOOP)
@R1
D = M //R1 will work as i, w ffhile i not 0 keep going.
@END
D;JEQ //if i == 0, we're done
@R0
D = M
@R2
M = M + D //Add R0 to sum
@R1
M = M - 1 //Reduce i
@LOOP
0;JMP
(END)
@END
0;JMP
