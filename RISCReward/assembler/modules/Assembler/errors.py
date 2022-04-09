import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import IO

from .memory import Memory

def openp(filepath: str) -> IO:
	return open(Path(__file__).with_name(filepath))

with openp('categories.json') as fl:
	cats = json.load(fl)
with openp('instructions.json') as fl:
	insts = json.load(fl)

@dataclass
class Error():
	text: str
	line: int

# checks if the command is broadly valid for the variant identified
def check_variant(variant: str, line: str, PC: int, started: bool) -> tuple[bool, list[Error]]:
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
		if len(params) == 0 or params[0] not in insts:  # if invalid instruction category
			errors.append(Error('Instruction missing or unidentified', PC))
	
	return (len(errors) > 0, errors)

REGNAMES = re.compile('R[0-6]')
FLAGS = 'FLAGS'

# returns the invalid registers from a list of register names
def invalid_registers(regs: list[str]) -> list[str]:
	return [x for x in regs if (not REGNAMES.fullmatch(x))]

# returns the invalid registers from a list of register names except flags are allowed
def invalid_registers_but_you_can_use_flags(regs: list[str]) -> list[str]:
	return [x for x in regs if not (REGNAMES.fullmatch(x) or x == FLAGS)]

# returns invalidity and issue in a given immediate
def invalid_imm(imm: str) -> tuple[bool, str]:
	if not imm[0] == '$':
		return (True, "immediate name must start with '$' symbol")
	elif not imm[1:].isdigit():
		return (True, f"{imm} is not a positive integer")
	elif int(imm[1:]) > 255:
		return (True, f"{imm} lies beyond the integer size limit")
	return (False, "no issue")

# checks if the command is strictly valid for the given category
def check_cat(opc: int, cat: str, line: str, mem: Memory, PC: int) -> tuple[bool, list[Error]]:
	params: list[str] = line.split()
	errors: list[Error] = []
	
	if cat == 'unidentified':
		errors.append(Error(f"Instruction {params[0]} not identified", PC))
		return (True, errors)
	
	l = len(params)
	l0 = len([x for x in cats[cat]['encoding'] if x != "unused"])
	if l0 != l:
		errors.append(Error(f"{l - 1} parameter/s given, but the {params[0]} instruction expects {l0 - 1}", PC))
	
	"""
	match cat:
		case 'A' | 'C':
			if opc == 0b00011:
				try:
					if len(invalid_registers([params[1]])) > 0:
						errors.extend([Error(f"invalid register name: {x}", PC) for x in invalid_registers([params[1]])])
					
					if len(invalid_registers_but_you_can_use_flags([params[2]])) > 0:
						errors.extend([Error(f"invalid register name: {x}", PC) for x in invalid_registers([params[2]])])
				except IndexError:
					pass
			
			else:
				try:
					if len(invalid_registers(params[1:])) > 0:
						errors.extend([Error(f"invalid register name: {x}", PC) for x in invalid_registers(params[1:])])
				except IndexError:
					pass
		
		case 'B':
			try:
				if len(invalid_registers([params[1]])) > 0:
					errors.extend([Error(f"invalid register name: {x}", PC) for x in invalid_registers([params[1]])])
				
				if invalid_imm(params[2])[0]:
					errors.append(Error(invalid_imm(params[2])[1], PC))
			except IndexError:
				pass
		
		case 'D':
			try:
				if len(invalid_registers([params[1]])) > 0:
					errors.extend([Error(f"invalid register name: {x}", PC) for x in invalid_registers([params[1]])])
				
				if not mem.has_var(params[2]):
					errors.append(Error(f"invalid variable name: {params[2]}", PC))
			except IndexError:
				pass
		
		case 'E':
			try:
				if not mem.has_label(params[1]):
					errors.append(Error(f"invalid label name: {params[1]}", PC))
			except IndexError:
				pass
	"""
	if cat == 'A' or cat == 'C':
		if opc == 0b00011:
			try:
				if len(invalid_registers([params[1]])) > 0:
					errors.extend([Error(f"invalid register name: {x}", PC) for x in invalid_registers([params[1]])])
				
				if len(invalid_registers_but_you_can_use_flags([params[2]])) > 0:
					errors.extend([Error(f"invalid register name: {x}", PC) for x in invalid_registers([params[2]])])
			except IndexError:
				pass
		
		else:
			try:
				if len(invalid_registers(params[1:])) > 0:
					errors.extend([Error(f"invalid register name: {x}", PC) for x in invalid_registers(params[1:])])
			except IndexError:
				pass
	
	elif cat == 'B':
		try:
			if len(invalid_registers([params[1]])) > 0:
				errors.extend([Error(f"invalid register name: {x}", PC) for x in invalid_registers([params[1]])])
			
			if invalid_imm(params[2])[0]:
				errors.append(Error(invalid_imm(params[2])[1], PC))
		except IndexError:
			pass
	
	elif cat == 'D':
		try:
			if len(invalid_registers([params[1]])) > 0:
				errors.extend([Error(f"invalid register name: {x}", PC) for x in invalid_registers([params[1]])])
			
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

# handles logging of errors in the code
class Logger():
	def __init__(self):
		self.log: list[str] = []
	
	# checks if there are any errors in the log
	def errors_present(self) -> bool:
		return len(self.log) > 0
	
	# adds a list of errors to the log
	def log_errors(self, lnum: int, errors: list[Error]):
		msg = f"ERROR/S spotted on Line {lnum}\n"
		for error in errors:
			msg += f"{error.text}\n"
		self.log.append(msg)
	
	# gets all errors in the log
	def get_errors(self) -> list[str]:
		return self.log
