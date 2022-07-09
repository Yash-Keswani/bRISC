from __future__ import annotations  # 3.9 Compatibility Hack
from ..base import Error, ISA
from ..imports import MockMemory as Memory
import json
import re

class ISA_FancyRISC(ISA):
	REGNAMES = re.compile('R[0-6]')
	FLAGS = 'FLAGS'

	def check_variant(self, variant: str, line: str, PC: int, started: bool) -> tuple[bool, list[Error]]:
		errors: list[Error] = []
		
		if variant == 'label':
			if line.count(':') >= 2:
				errors.append(Error('The ":" symbol cannot be used multiple times in the same line', PC))
			if line[line.index(':') - 1] == ' ':
				errors.append(Error('Label has whitespace before :', PC))
		if variant == 'variable':
			if started:
				errors.append(Error('Variable defined after start of program', PC))
		if variant == 'instruction':
			params = line.split()
			if len(params) == 0 or params[0] not in self.insts:  # if invalid instruction category
				errors.append(Error('Instruction missing or unidentified', PC))
		
		return (len(errors) > 0, errors)

	# returns the invalid registers from a list of register names
	def invalid_registers(self, regs: list[str]) -> list[str]:
		return [x for x in regs if (not self.REGNAMES.fullmatch(x))]

	# returns the invalid registers from a list of register names except flags are allowed
	def invalid_registers_but_you_can_use_flags(self, regs: list[str]) -> list[str]:
		return [x for x in regs if not (self.REGNAMES.fullmatch(x) or x == self.FLAGS)]

	# returns invalidity and issue in a given immediate
	@staticmethod
	def invalid_imm(imm: str) -> tuple[bool, str]:
		if not imm[0] == '$':
			return (True, "immediate name must start with '$' symbol")
		elif not imm[1:].isdigit():
			return (True, f"{imm} is not a positive integer")
		elif int(imm[1:]) > 255:
			return (True, f"{imm} lies beyond the integer size limit")
		return (False, "no issue")

	# checks if the command is strictly valid for the given category
	def check_cat(self, opc: int, cat: str, line: str, mem: Memory, PC: int) -> tuple[bool, list[Error]]:
		params: list[str] = line.split()
		errors: list[Error] = []
		
		if cat == 'unidentified':
			errors.append(Error(f"Instruction {params[0]} not identified", PC))
			return (True, errors)
		
		l = len(params)
		l0 = len([x for x in self.cats[cat]['encoding'] if x != "unused"])
		if l0 != l:
			errors.append(Error(f"{l - 1} parameter/s given, but the {params[0]} instruction expects {l0 - 1}", PC))
		
		if cat == 'A' or cat == 'C':
			if opc == 0b00011:
				try:
					if len(self.invalid_registers([params[1]])) > 0:
						errors.extend([Error(f"invalid register name: {x}", PC) for x in self.invalid_registers([params[1]])])
					
					if len(self.invalid_registers_but_you_can_use_flags([params[2]])) > 0:
						errors.extend([Error(f"invalid register name: {x}", PC) for x in self.invalid_registers([params[2]])])
				except IndexError:
					pass
			
			else:
				try:
					if len(self.invalid_registers(params[1:])) > 0:
						errors.extend([Error(f"invalid register name: {x}", PC) for x in self.invalid_registers(params[1:])])
				except IndexError:
					pass
		
		elif cat == 'B':
			try:
				if len(self.invalid_registers([params[1]])) > 0:
					errors.extend([Error(f"invalid register name: {x}", PC) for x in self.invalid_registers([params[1]])])
				
				if self.invalid_imm(params[2])[0]:
					errors.append(Error(self.invalid_imm(params[2])[1], PC))
			except IndexError:
				pass
		
		elif cat == 'D':
			try:
				if len(self.invalid_registers([params[1]])) > 0:
					errors.extend([Error(f"invalid register name: {x}", PC) for x in self.invalid_registers([params[1]])])
				
				if not mem.has_var(params[2]):
					errors.append(Error(f"invalid variable name: {params[2]}", PC))
			except IndexError:
				pass
		
		elif cat == 'E':
			try:
				if not mem.has_label(params[1]):
					errors.append(Error(f"invalid label name: {params[1]}", PC))
			except IndexError:
				pass
		
		return (len(errors) > 0, errors)

	# find what variant of command is present in this line, and return it
	def find_variant(self, line: str) -> str:
		if line == '':
			return 'blank'
		elif ':' in line[1:]:
			return 'label'
		elif line.startswith('var'):
			return 'variable'
		return 'instruction'

	# finds what category a specific command belongs to, and its opcode
	def find_cat(self, cmd: str) -> dict[str, int | str]:
		params = cmd.split()
		if len(params) == 0 or params[0] not in self.insts:  # if invalid instruction category
			return {'opcode': 0b11111, 'cat': 'unidentified'}
		
		opcode = int(self.insts[params[0]][0]['opcode'], base=2)
		cat = self.insts[params[0]][0]['type']
		
		if len(self.insts[params[0]]) > 1:  # very sloppy hard coding for mov instruction
			if params[2][0] != '$':
				opcode = int(self.insts[params[0]][1]['opcode'], base=2)
				cat = self.insts[params[0]][1]['type']
		
		# return cat
		return {'opcode': opcode, 'cat': cat}

	# encodes command according to its category
	def encode(self, opc: int, ctg: str, cmd: str, mem: Memory) -> str:
		params = cmd.split()
		toret = ""
		if ctg == 'A':
			toret += f'{opc:05b}'  # opc = 0 => 0 to 5 bit binary => 00000
			toret += f'{0:02b}'  # unused 2 bits => 0 to 2 bit binary => 00
			toret += f'{int(params[1][1]):03b}'  # R0 => 0 => 0 to 3 bit binary => 000
			toret += f'{int(params[2][1]):03b}'  # R1 => 1 => 1 to 3 bit binary => 001
			toret += f'{int(params[3][1]):03b}'  # R2 => 2 => 2 to 3 bit binary => 010
		
		elif ctg == 'B':
			toret += f'{opc:05b}'
			toret += f'{int(params[1][1]):03b}'
			toret += f'{int(params[2][1:]):08b}'
		
		elif ctg == 'C':
			toret += f'{opc:05b}'
			toret += f'{0:05b}'
			toret += f'{int(params[1][1]):03b}'
			try:
				toret += f'{int(params[2][1]):03b}'
			except ValueError:
				toret += f'{7:03b}'
		
		elif ctg == 'D':
			toret += f'{opc:05b}'
			toret += f'{int(params[1][1]):03b}'
			toret += f'{mem.var_addr(params[2]):08b}'
		
		elif ctg == 'E':
			toret += f'{opc:05b}'
			toret += f'{0:03b}'
			toret += f'{mem.label_addr(params[1]):08b}'
		
		elif ctg == 'F':
			toret += f'{opc:05b}'
			toret += f'{0:011b}'
		
		return toret
