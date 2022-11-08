import json
from pathlib import Path
from typing import IO

from .storage import Memory, Registry

def openp(filepath: str) -> IO:
	return open(Path(__file__).parent.__str__() + filepath)

def lookup(data: dict[list[dict]], opc: int) -> dict:
	for inst in data.values():
		for style in inst:
			if int(style["opcode"][2:], base=2) == opc:
				return style

class CU:
	with openp('/../ISA_Specs/instructions.json') as fl:
		insts = json.load(fl)
	
	# returns the opcode of a line
	@staticmethod
	def get_opcode(line: str):
		"""
		input:
		line -> 32 bit binary string
		
		output:
		return list[int]
		up to 3 things returned - opcode, funct3, funct7
		
		TODO: naman shivam sunishka
		"""
		return int(line[0:5], base=2)
	
	# returns the type of the command from its opcode
	@classmethod
	def get_type_from_opcode(cls, opc: int) -> str:
		"""
		input:
		opcode: int
		
		output:
		return string with type
		
		TODO: sunishka
		"""
		for inst in cls.insts:  # Iterates through each instruction name
			for form in cls.insts[inst]:  # Iterates through forms of each instruction
				if form['opcode'].endswith(f'{opc:05b}'):
					return form['type']
	
	# gets the opcode and category of the command
	@classmethod
	def interpret(cls, line: str) -> tuple[int, str]:
		opc = cls.get_opcode(line)
		return opc, cls.get_type_from_opcode(opc)
	
	# gets the values used as source operand/s by a line of code
	@classmethod
	def fetch_sources(cls, cat: str, line: str, mem: Memory, reg: Registry) -> list[int]:
		"""
		cat -> type [R, S, I, SB]
		line -> binary string: 32-bit
		
		TODO: naman shivam
		return rs1, rs2, imm
		"""
		if cat == 'A':
			sources = [
				reg.read_reg(int(line[10:13], base=2)),
				reg.read_reg(int(line[13:], base=2))
			]
		elif cat == 'B':
			sources = [
				reg.read_reg(int(line[5:8], base=2)),
				int(line[8:], base=2)
			]
			locs = [
				int(line[5:8], base=2)
			]
		elif cat == 'C':
			sources = [
				reg.read_reg(int(line[10:13], base=2)),
				reg.read_reg(int(line[13:], base=2))
			]
			locs = [
				int(line[10:13], base=2),
				int(line[13:], base=2)
			]
		elif cat == 'D':
			sources = [
				reg.read_reg(int(line[5:8], base=2)),
				mem.read_loc(int(line[8:], base=2))
			]
			locs = [
				int(line[5:8], base=2),
				int(line[8:], base=2)
			]
		elif cat == 'E':
			sources = [
				int(line[8:], base=2),
				reg.read_reg(7)  # subjected to locking and unlocking
			]
			locs = [
				int(line[8:], base=2)
			]
		else:
			sources = locs = []
		
		return sources
	
	# gets the values used as destination operand/s by a line of code
	@classmethod
	def fetch_destinations(cls, cat: str, line: str) -> list:
		"""
		cat -> type [R, I, S, SB]
		line -> 32 bit binary string
		
		destination -> rd  [register number, or immediate (mem address)]
		
		TODO: naman shivam sunishka
		"""
		if cat == 'A':
			dests = [
				int(line[7:10], base=2)
			]
		elif cat == 'B':
			dests = [
				int(line[5:8], base=2)
			]
		elif cat == 'C':
			if opc == 0b00111:
				dests = [0, 1]
			else:
				dests = [
					int(line[10:13], base=2),
					int(line[13:], base=2)
				]
		elif cat == 'D':
			dests = [
				int(line[5:8], base=2),
				int(line[8:], base=2)
			]
		else:
			dests = []
		
		for i in range(len(dests)):
			if i not in lookup(cls.insts, opc)["dest"]:
				dests[i] = -1
		return dests
	
	# handles output after execution is done. returns whether or not there are lines afterwards.
	@staticmethod
	def store_results_reg(dests, output, opc: int, cat: str, reg: Registry) -> None:
		reg.set_flags(output['flags'])
		if cat in ['A', 'B']:
			reg.write_reg(dests[0], output['main'])
		elif cat == 'C':
			if opc in (0b00011, 0b01101):  # mov / not
				reg.write_reg(dests[0], output['main'])
			elif opc == 0b00111:  # div
				reg.write_reg(0, output['main'])
				reg.write_reg(1, output['alter'])
		elif cat == 'D':
			if not opc & 1:
				reg.write_reg(dests[0], output['main'])
	
	# stores any relevant results into the memory
	@staticmethod
	def store_results_mem(dests, output, opc, cat, mem: Memory) -> None:
		if opc & 1 and cat == 'D':
			mem.write_loc(dests[1], output['main'])
	
	# branches to next instruction of PC
	@staticmethod
	def next_instruction(output: dict, reg: Registry) -> bool:
		if output['branch']:
			reg.branch_to(output['main'])
			return True
		else:
			return False
