# Helper class for the HackAssembler, only translates 1 instruction at a time.
# Does not process symbols, jumps or builtins, as that's the other class' job.

import re

# Map of values for a D instruction

OP_PINS = "111"
C_VALUES = {"0": "101010", "1": "111111", "-1": "111010", "D": "001100", "X": "110000",
            "!D": "001101", "!X": "110001", "-D": "001111", "-X": "110011",
            "D+1": "011111", "X+1": "110111", "D-1": "001110", "X-1": "110010",
            "D+X": "000010", "D-X": "010011", "X-D": "000111", "D&X": "000000", "D|X": "010101"}
D_POSITIONS = {"A": "0", "D": "1", "M": "2"}
J_VALUES = {"JGT": "001", "JEQ": "010", "JGE": "011",
            "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"}


class InstructionAssembler(object):
    def __init__(self, instruction):
        self.instruction = instruction
        # Determines the type of the instruction.
        if instruction.startswith("@"):
            self.ins_type = "A"
        else:
            self.ins_type = "C"
        # If it's C it needs extra variables.
        if self.ins_type == "C":
            self.a_bit = self.Comp_bits = self.Dest_bits = self.Jump_bits = None
            self.comp = self.dest = self.jump = None

    def set_CPins(self, instruction):
        '''
        Sorts all pins from a C instruction, setting all their values.
        instruction: string. A hack C instruction.
        '''
        # Structure is Dest=Comp;Jump where dest and jump are optional.
        if instruction.find("=") != -1:
            self.dest, self.comp = instruction.split("=", 1)
            instruction = self.comp
        if instruction.find(";") != -1:
            self.comp, self.jump = instruction.split(";", 1)
        if not self.dest and not self.jump:
            self.comp = instruction

    def assemble_a_bit(self, comp):
        '''
        Checks if it's the A or M register that is being used in a C type instruction.
        c: string. Comp bits in a C instruction.
        returns: 0 if A is used, 1 if M is used.
        '''
        if comp.find("M") != -1:
            return "1"
        return "0"

    def assemble_comp(self, comp):
        '''
        Translates comp bits to the binary bits which determine the process the ALU does.
        c: string. Comp bits in a C instruciton.
        returns: string. Binary value of comp pins for the given instruction or ERROR if it fails.
        '''
        C_bits = None
        # Replace A and M to X so that they're interchangeable as they're both the same for the ALU.
        c = re.sub("[AM]", "X", comp)
        # Check if the comp is in the possible comp values.
        # If not check if reverse is, as long as it's not a subtraction, they're commutable.
        if c in C_VALUES.keys():
            C_bits = C_VALUES[c]
        elif c[::-1] in C_VALUES.keys() and c.find("-") == -1:
            C_bits = C_VALUES[c[::-1]]
        else:
            # Error wrong c_code.
            return "ERRORc."
        return C_bits

    def assemble_dest(self, dest):
        '''
        Translates destination bits into binary, determines where to store the ALU result.
        d: string. Destination bits in a C instruction.
        returns: string. Binary value of the destination bits or ERROR on failure.
        '''
        if not dest:
            return "000"
        D_bits = None
        if len(set(dest)) != len(dest):
            # Error, invalid dest_code, duplicate register dest.
            return "ERRORd."
        else:
            D_bits = "000"
            for d in dest:
                if d not in D_POSITIONS.keys():
                    # Error, invalid dcode, dest is not a valid register.
                    return "ERRORd."
                # If register is a dest, take the position value in pins and set it to 1.
                i = int(D_POSITIONS[d])
                D_bits = D_bits[:i] + "1" + D_bits[i+1:]
        return D_bits

    def assemble_jump(self, jump):
        '''
        Translate jump bits into binary, these check against 0 to tell PC whether
        to jump to A register's value.
        j: string. Jump bits in a C instruction.
        returns: string. Binary value of the jump bits or ERROR on failure.
        '''
        if not jump:
            return "000"
        J_bits = None
        if jump not in J_VALUES.keys():
            # Error, invalid j code
            return "ERRORj."
        else:
            J_bits = J_VALUES[jump]
        return J_bits

    def assemble_C(self, instruction):
        '''
        Assembles the C instruction, assembling all pins and adding them in the correct order.
        instruction: string. C Type instruction.
        '''
        self.set_CPins(self.instruction)
        self.a_bit = self.assemble_a_bit(self.comp)
        self.Comp_bits = self.assemble_comp(self.comp)
        self.Dest_bits = self.assemble_dest(self.dest)
        self.Jump_bits = self.assemble_jump(self.jump)
        binaryInstruction = OP_PINS + self.a_bit + self.Comp_bits\
            + self.Dest_bits + self.Jump_bits
        self.binaryInstruction = binaryInstruction

    def assemble_A(self, instruction):
        instruction = int(self.instruction[1:])
        if instruction > 32767:
            self.binaryInstruction = "ERRORob."
        instruction = "0" + "{0:015b}".format(instruction)
        self.binaryInstruction = instruction

    def assemble(self):
        '''
        Translates the loaded instruction into binary, whether it's A or D type.
        returns: int. Value of the instruction in binary.
        '''
        if self.ins_type == "C":
            self.assemble_C(self.instruction)
        else:
            # Assemble A
            self.assemble_A(self.instruction)
        error = re.search("ERROR(\w)", self.binaryInstruction)
        if error:
            return error.group(1)
        return self.binaryInstruction
