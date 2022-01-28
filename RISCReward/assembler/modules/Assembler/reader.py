import json
from pathlib import Path
from typing import IO

from .memory import Memory

def openp(filepath: str) -> IO:
	return open(Path(__file__).with_name(filepath))

with openp('categories.json') as fl:
	cats = json.load(fl)
with openp('instructions.json') as fl:
	insts = json.load(fl)

# find what variant of command is present in this line, and return it
def find_variant(line: str) -> str:
	if line == '':
		return 'blank'
	elif ':' in line[1:]:
		return 'label'
	elif line.startswith('var'):
		return 'variable'
	return 'instruction'

# finds what category a specific command belongs to, and its opcode
def find_cat(cmd: str) -> dict[str, int | str]:
	params = cmd.split()
	if len(params) == 0 or params[0] not in insts:  # if invalid instruction category
		return {'opcode': 0b11111, 'cat': 'unidentified'}
	
	opcode = int(insts[params[0]][0]['opcode'], base=2)
	cat = insts[params[0]][0]['type']
	
	if len(insts[params[0]]) > 1:  # very sloppy hard coding for mov instruction
		if params[2][0] != '$':
			opcode = int(insts[params[0]][1]['opcode'], base=2)
			cat = insts[params[0]][1]['type']
	
	# return cat
	return {'opcode': opcode, 'cat': cat}

# encodes command according to its category
def encode(opc: int, ctg: str, cmd: str, mem: Memory) -> str:
	params = cmd.split()
	toret = ""
	# add R0 R1 R2 => params = ['add','R0','R1','R2']
	
	match ctg:
		case 'A':
			toret += f'{opc:05b}'  # opc = 0 => 0 to 5 bit binary => 00000
			toret += f'{0:02b}'  # unused 2 bits => 0 to 2 bit binary => 00
			toret += f'{int(params[1][1]):03b}'  # R0 => 0 => 0 to 3 bit binary => 000
			toret += f'{int(params[2][1]):03b}'  # R1 => 1 => 1 to 3 bit binary => 001
			toret += f'{int(params[3][1]):03b}'  # R2 => 2 => 2 to 3 bit binary => 010
		# toret = "0000000000001010"
		
		case 'B':
			toret += f'{opc:05b}'
			toret += f'{int(params[1][1]):03b}'
			toret += f'{int(params[2][1:]):08b}'
		
		case 'C':
			toret += f'{opc:05b}'
			toret += f'{0:05b}'
			toret += f'{int(params[1][1]):03b}'
			try:
				toret += f'{int(params[2][1]):03b}'
			except ValueError:
				toret += f'{7:03b}'
		
		case 'D':
			toret += f'{opc:05b}'
			toret += f'{int(params[1][1]):03b}'
			toret += f'{mem.var_addr(params[2]):08b}'
		
		case 'E':
			toret += f'{opc:05b}'
			toret += f'{0:03b}'
			toret += f'{mem.label_addr(params[1]):08b}'
		
		case 'F':
			toret += f'{opc:05b}'
			toret += f'{0:011b}'
	
	return toret
