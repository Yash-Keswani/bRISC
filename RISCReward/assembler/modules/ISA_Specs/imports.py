import json
from dataclasses import dataclass
from enum import Enum
from typing import IO

class Bundle:
	datadict = {}
	
	def to_dict(self) -> dict:
		return self.datadict
	
	@staticmethod
	def loadDict(inp: dict):
		toret = Bundle()
		for k, v in inp.items():
			if isinstance(v, dict):
				setattr(toret, k, Bundle.loadDict(v))
			else:
				setattr(toret, k, v)
			toret.datadict[k] = v
		return toret
		

def openp(filepath: str) -> IO:
	return open(f'assembler/modules/ISA_Specs/{CONF.IMPORTED_ISA}/' + filepath)

class CONF:
	conf = None
	opcodes = None
	insts = None
	cats = None
	IMPORTED_ISA = ''

	@classmethod
	def reload(cls, _isa: str):
		cls.IMPORTED_ISA = _isa
		with openp("system_specifications.json") as fp:
			cls.conf = Bundle.loadDict(json.load(fp))
		with openp("ins_decode.json") as fp:
			cls.opcodes = [int(x[2:], base=2) for x in json.load(fp).keys()]
		with openp("ins_encode.json") as fp:
			cls.insts = json.load(fp)
		with openp("categories.json") as fp:
			cls.cats = json.load(fp)

@dataclass
class Error():
	text: str
	
	def __str__(self):
		return self.text

class ErrorLogger():
	lno: int = -1
	err: list[list[Error]] = []
	err_buffer: list[Error] = []
	
	@classmethod
	def tick(cls):
		cls.lno += 1
		cls.err.append([])
		cls.buf_dump()
	
	@classmethod
	def get_err(cls):
		return cls.err
		
	@classmethod
	def buf_log(cls, err_str: str):
		cls.err[cls.lno].append(Error(err_str))
		
	@classmethod
	def buf_flush(cls):
		cls.err[cls.lno].extend(cls.err_buffer)
	
	@classmethod
	def buf_dump(cls):
		cls.err[cls.lno] = []
	
	@classmethod
	def log(cls, err_str: str):
		cls.err[cls.lno].append(Error(err_str))
	
	@classmethod
	def dump(cls):
		cls.err[cls.lno] = []

class Variant(Enum):
	var="variable"
	ins="instruction"
	lab="label"
	blank="blank"

# maintains a mock memory for the assembler
class MockMemory():
	mem: int = -1  # where will the next variable be added
	mem_labels: dict[str, int] = {}  # PC of all labels
	mem_vars: dict[str, int] = {}  # memory address of all variables
	
	# loads memory from a specific starting pointer
	@classmethod
	def load(cls, start_ptr: int):
		cls.mem = start_ptr
	
	# checks if a certain label is present in the memory
	@classmethod
	def has_label(cls, name: str) -> bool:
		return name in cls.mem_labels
	
	# checks if a certain variable is present in the memory
	@classmethod
	def has_var(cls, name: str) -> bool:
		return name in cls.mem_vars
	
	# returns the memory address of a named label
	@classmethod
	def label_addr(cls, name: str) -> int:
		assert cls.has_label(name), "label not present in memory"
		return cls.mem_labels[name]
	
	# returns the memory address of a named variable
	@classmethod
	def var_addr(cls, name: str) -> int:
		assert cls.has_var(name), "variable not present in memory"
		return cls.mem_vars[name]
	
	# stores a label with the PC to which it corresponds
	@classmethod
	def store_label(cls, name: str, PC: int) -> None:
		cls.mem_labels[name] = PC
	
	# stores a variable with the memory location to which it corresponds
	@classmethod
	def store_var(cls, name: str) -> None:
		cls.mem_vars[name] = cls.mem
		cls.mem += 1
