import json
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import IO

@dataclass
class Error():
	text: str
	line: int

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

	@classmethod
	@abstractmethod
	def check_variant(cls, variant: str, line: str, PC: int, started: bool) -> tuple[bool, list[Error]]:
		pass
	
	@classmethod
	@abstractmethod
	def check_cat(cls, opc: int, cat: str, line: str, mem: MockMemory, PC: int) -> tuple[bool, list[Error]]:
		pass
	
	@classmethod
	@abstractmethod
	def encode(cls, opc: int, ctg: str, cmd: str, mem: MockMemory) -> str:
		pass

	@classmethod
	@abstractmethod
	def find_cat(cls, cmd: str) -> dict[str, int | str]:
		pass
	
	@classmethod
	@abstractmethod
	def find_variant(cls, line: str) -> str:
		pass
