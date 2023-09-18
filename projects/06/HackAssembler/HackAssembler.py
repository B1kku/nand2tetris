# Main file of the Hack Assembler, translates hack assembly into hack binary code.
# Assignment assumed the code to assemble will be clean from errors, still added some.
# Usage: python HackAssembler.py inputfile [outputfile]

import re
import sys
import pathlib
import time
from InstructionAssembler import InstructionAssembler as Assembler

PREDIFINED_SYMBOLS = {
    "SP": "0", "LCL": "1", "ARG": "2", "THIS": "3", "THAT": "4",
    "SCREEN": "16384", "KEYBOARD": "24576"}
for iterator in range(15+1):
    iterator = str(iterator)
    PREDIFINED_SYMBOLS["R"+iterator] = iterator
VAR_START = 16

ERRORS = {"c": "invalid comp value in C instruction.",
          "d": "invalid dest value in C instruction.",
          "j": "invalid jump value in C instruction.",
          "ob": "A instruction is out of bounds.",
          "dj": "jump destination already exists.",
          "1A": "first instruction must be an A instruction."}


class HackAssembler(object):
    def __init__(self, instructions):
        self.original = instructions
        self.instructions = instructions
        self.locations = {}
        self.variables_found = {}
        self.user_symbols = {}
        self.padding = 0

    def fail(self, line, error):
        print("Error assembling", self.original[line], "on line", line+1)
        print("Error:", ERRORS[error])
        exit(-5)

    def cleanIgnored(self, instruction):
        '''
        Deletes all does not convey any information for the compiler (whitespace and comments).
        instruction: string. Hack instruction to clean.
        returns: string. Instruction cleaned.
        '''
        return re.sub(r"\s|//.*", "", instruction)

    def registerLocation(self, location, nline):
        '''
        Adds a location alias to the list, needs padding to know the real address to register it with,
        instruction: string. A location alias, ex:"(LOOP)"
        returns: Error or empty string.
        '''
        # Strip the () off
        location = location[1:len(location) - 1]
        # If the location was already registered, fail.
        if location in self.locations.keys():
            self.fail(nline, "ERRORdl.")
        # Key is the loc name, value is the real address in ROM (current - blanklines and jumps)
        self.locations[location] = nline - self.padding
        self.padding += 1
        return ""

    def registerVarOccurrence(self, variable, nline):
        '''
        Registers the variable and the line it happened on for later processing.
        variable: string. A hack variable ex:"@tmp", note: case insensitive.
        nline: int. Line number it was found on.
        '''
        variable = variable[1:]
        self.variables_found[nline] = variable

    def replaceSymbols(self):
        '''
        Replaces every symbol on the instruction list with their address.
        Must register user_symbols, locations for jumps and occurrences first.
        '''
        # Dictionary holds every time a symbol was found and where, get the address
        # of that symbol and set it as "@Address" of that instruction.
        for k, v in self.variables_found.items():
            struct = None
            if v in PREDIFINED_SYMBOLS.keys():
                struct = PREDIFINED_SYMBOLS
            elif v in self.locations.keys():
                struct = self.locations
            elif v in self.user_symbols.keys():
                struct = self.user_symbols
            else:
                self.user_symbols[v] = VAR_START + len(self.user_symbols.keys())
                struct = self.user_symbols
            self.instructions[int(k)] = "@" + str(struct[v])

    def preprocess(self):
        '''
        Preprocesses the loaded instruction list, removing all comments and whitespace.
        Also replaces symbols with their respective address.
        Keeps empty lines to know real address of jumps.
        '''
        for i, instruction in enumerate(self.instructions):
            instruction = self.cleanIgnored(instruction)
            if not instruction:
                self.padding += 1
            elif instruction.startswith("("):
                instruction = self.registerLocation(instruction, i)
            elif instruction.startswith("@") and not instruction[1:].isnumeric():
                self.registerVarOccurrence(instruction, i)
            self.instructions[i] = instruction
        self.replaceSymbols()

    def assembleAll(self):
        '''
        Preprocesses the code, checks first instruction is A and passes them through the assembler.
        '''
        self.preprocess()
        binary_instructions = []
        first_ins_flag = False
        for i, instruction in enumerate(self.instructions):
            if not instruction:
                continue
            if not first_ins_flag:
                first_ins_flag = True
                if not instruction.startswith("@"):
                    self.fail(i, "1A")
                    return
            instruction = Assembler(instruction).assemble()
            if instruction in ERRORS.keys():
                self.fail(i, instruction)
            binary_instructions.append(instruction)
        return binary_instructions


if __name__ == "__main__":
    timerStart = time.time()
    argc = len(sys.argv)
    instructions = []
    if argc == 1 or argc > 3:
        print("Usage: python HackAssembler.py input [output]")
        exit(-1)
    infile = pathlib.Path(sys.argv[1])
    outfile = pathlib.Path(infile.parent, (infile.stem + ".hack"))
    if infile.suffix != ".asm":
        print("Invalid file type, got:" + '"' + infile.suffix + '".', "Required:\".asm\"")
        exit(-1)
    try:
        with open(infile) as fhandle:
            instructions = HackAssembler(fhandle.readlines()).assembleAll()
    except FileNotFoundError:
        print("Invalid file path.")
        exit(-2)
    except PermissionError:
        print("Invalid file permissions.")
        exit(-2)
    if argc == 3:
        outfile = pathlib.Path(sys.argv[2])
    try:
        with open(outfile, "w") as fhandle:
            for instruction in instructions:
                fhandle.write(instruction + "\n")
        timerEnd = time.time() - timerStart
        print("Success :), translated", len(instructions), "instructions to",
              outfile.stem + outfile.suffix + " in", "{0:.4f}".format(timerEnd) + "s")
        exit(0)
    except PermissionError:
        print("Invalid permissions, could not create output file.")
        exit(-3)
