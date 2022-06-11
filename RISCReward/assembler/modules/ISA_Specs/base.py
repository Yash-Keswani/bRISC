import json
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import IO
from .imports import conf, opcodes, insts

from .rules import Rule, ValidGeneralRegister, ValidSpecialRegister, ValidOpcode,	ValidFlagsRegister, ValidHeapMemoryAddress

@dataclass
class Error():
	text: str
	line: int

class Token(ABC):
	@property
	@abstractmethod
	def rules(self) -> list[list[Rule]]:
		raise NotImplementedError
	
	def __init__(self, _value: int | str, _size: int):
		self.value: int | str = _value
		self.size: int = _size

	def verify(self) -> bool:
		for ruleset in self.rules:
			if not any((x.check(self.value) for x in ruleset)):
				return False
		return True
	
	def encode(self) -> str:
		return f"{self.value: 0{self.size}b}"

class RegisterSrc(Token):
	def __init__(self, _value, _size):
		super().__init__(_value, _size)
	rules: list[Rule] = [[ValidGeneralRegister, ValidSpecialRegister, ValidFlagsRegister]]
	
	def encode(self) -> str:
		num = int(self.value.lstrip(conf.instructions.prefixes.register))
		return f"{num:0{self.size}b}"
	
class RegisterDest(Token):
	def __init__(self, _value, _size):
		super().__init__(_value, _size)
	rules: list[Rule] = [[ValidGeneralRegister, ValidSpecialRegister]]
	
	def encode(self) -> str:
		num = int(self.value.lstrip(conf.instructions.prefixes.register))
		return f"{num:0{self.size}b}"

class OpCode(Token):
	def __init__(self, _value, _size):
		super().__init__(_value, _size)
	rules: list[Rule] = [[ValidOpcode]]

class MemAddress(Token):
	def __init__(self, _value, _size):
		super().__init__(_value, _size)
	rules: list[Rule] = [[ValidHeapMemoryAddress]]
	

# maintains a mock memory for the assembler
class MockMemory():
	def __init__(self, start_ptr: int):
		self.mem: int = start_ptr  # where will the next variable be added
		self.mem_labels: dict[str, int] = {}  # PC of all labels
		self.mem_vars: dict[str, int] = {}  # memory address of all variables
	
	# checks if a certain label is present in the memory
	def has_label(self, name: str) -> bool:
		return name in self.mem_labels
	
	# checks if a certain variable is present in the memory
	def has_var(self, name: str) -> bool:
		return name in self.mem_vars
	
	# returns the memory address of a named label
	def label_addr(self, name: str) -> int:
		assert self.has_label(name), "label not present in memory"
		return self.mem_labels[name]
	
	# returns the memory address of a named variable
	def var_addr(self, name: str) -> int:
		assert self.has_var(name), "variable not present in memory"
		return self.mem_vars[name]
	
	# stores a label with the PC to which it corresponds
	def store_label(self, name: str, PC: int) -> None:
		self.mem_labels[name] = PC
	
	# stores a variable with the memory location to which it corresponds
	def store_var(self, name: str) -> None:
		self.mem_vars[name] = self.mem
		self.mem += 1

class ISA(ABC):
	def __init__(self):
		def openp(filepath: str) -> IO:
			return open(Path(sys.modules[self.__module__].__file__).with_name(filepath))
		
		with openp("ins_encode.json") as fp:
			self.insts = json.load(fp)
		with openp("categories.json") as fp:
			self.cats = json.load(fp)
		with openp("system_specifications.json") as fp:
			self.conf = json.load(fp)

	@classmethod
	@abstractmethod
	def check_variant(cls, variant: str, line: str, PC: int, started: bool) -> tuple[bool, list[Error]]:
		pass
	
	def tokenise(self, line: str) -> list[Token]:
		pass
	
	@classmethod
	@abstractmethod
	def check_cat(cls, opc: int, cat: str, line: str, mem: MockMemory, PC: int) -> tuple[bool, list[Error]]:
		pass
	
	def encode(self, opc: int, ctg: str, cmd: str, mem: MockMemory) -> str:
		tokens = cmd.split()
		toret = ""
		encoding: dict[str, int] = self.cats[tokens[0]]
		
		start: int = 0
		for parameter in encoding:
			if parameter == "padding":
				continue
		
		if ctg == 'A':
			toret += f'{opc:05b}'  # opc = 0 => 0 to 5 bit binary => 00000
			toret += f'{0:02b}'  # unused 2 bits => 0 to 2 bit binary => 00
			toret += f'{int(tokens[1][1]):03b}'  # R0 => 0 => 0 to 3 bit binary => 000
			toret += f'{int(tokens[2][1]):03b}'  # R1 => 1 => 1 to 3 bit binary => 001
			toret += f'{int(tokens[3][1]):03b}'  # R2 => 2 => 2 to 3 bit binary => 010
		
		elif ctg == 'B':
			toret += f'{opc:05b}'
			toret += f'{int(tokens[1][1]):03b}'
			toret += f'{int(tokens[2][1:]):08b}'
		
		elif ctg == 'C':
			toret += f'{opc:05b}'
			toret += f'{0:05b}'
			toret += f'{int(tokens[1][1]):03b}'
			try:
				toret += f'{int(tokens[2][1]):03b}'
			except ValueError:
				toret += f'{7:03b}'
		
		elif ctg == 'D':
			toret += f'{opc:05b}'
			toret += f'{int(tokens[1][1]):03b}'
			toret += f'{mem.var_addr(tokens[2]):08b}'
		
		elif ctg == 'E':
			toret += f'{opc:05b}'
			toret += f'{0:03b}'
			toret += f'{mem.label_addr(tokens[1]):08b}'
		
		elif ctg == 'F':
			toret += f'{opc:05b}'
			toret += f'{0:011b}'
		
		return toret
	
	@classmethod
	@abstractmethod
	def find_cat(cls, cmd: str) -> dict[str, int | str]:
		pass
	
	@classmethod
	@abstractmethod
	def find_variant(cls, line: str) -> str:
		pass
