from __future__ import annotations  # 3.9 Compatibility Hack
from abc import ABC, abstractmethod

from .imports import CONF, ErrorLogger
from .rules import Rule, ValidGeneralRegister, ValidSpecialRegister, \
	ValidFlagsRegister, ValidInstruction, ValidDataPtr, ValidInsPtr, ValidRegister, ValidVariable, ValidLabel, ValidImm

class Token(ABC):
	silent = False
	
	@property
	@abstractmethod
	def rules(self) -> list[list[Rule]]:
		raise NotImplementedError
	
	def __init__(self, _value: int | str, _size: int):
		self.value: int | str = _value
		self.size: int = _size
	
	def verify(self) -> bool:
		passing = True
		for ruleset in self.rules:
			for rule in ruleset:
				passing, processed = rule.check(self.value)
				if passing and processed is not None:  # if any rule in ruleset passed
					self.value = processed
					break  # check next ruleset
			if not passing:
				ErrorLogger.buf_flush()  # if any rule fails,
				return False
		ErrorLogger.buf_dump()
		return True
	
	def encode(self) -> str:
		return f"{self.value:0{self.size}b}"

class RegSrc(Token):
	def __init__(self, _value, _size):
		super().__init__(_value, _size)
	
	rules = [[ValidRegister], [ValidGeneralRegister, ValidSpecialRegister, ValidFlagsRegister]]
	
	def encode(self) -> str:  # Stays because idk if reg is string or
		return f"{int(self.value):0{self.size}b}"

class RegDest(Token):
	def __init__(self, _value, _size):
		super().__init__(_value, _size)
	
	rules = [[ValidRegister], [ValidGeneralRegister, ValidSpecialRegister]]
	
	def encode(self) -> str:
		return f"{int(self.value):0{self.size}b}"

class Inst(Token):
	def __init__(self, _value, _size):
		super().__init__(_value, _size)
		if self.verify():
			self.patterns = [(x["opcode"], CONF.cats[x["type"]]) for x in CONF.insts[self.value]]
		else:
			self.pattern = None
	
	rules = [[ValidInstruction]]
	
	def encode(self):
		pass
	
	def pattern(self):
		pass

class OpCode(Token):
	def __init__(self, _value, _size):
		super().__init__(int(_value), _size)
	
	rules = []

class ImmInsPtr(Token):
	def __init__(self, _value, _size):
		super().__init__(_value, _size)
	
	rules = [[ValidInsPtr]]

class ImmDataPtr(Token):
	def __init__(self, _value, _size):
		super().__init__(_value, _size)
	
	rules = [[ValidDataPtr]]

class Switcher(Token):
	def __init__(self, _value, _size):
		super().__init__(_value, _size)
	
	rules = [[ValidDataPtr]]

class Modifier(Token):
	def __init__(self, _value, _size):
		super().__init__(_value, _size)
	
	rules = [[ValidDataPtr]]

class Padding(Token):
	silent = True
	
	def __init__(self, _value, _size):
		super().__init__(0, _size)
	
	rules = []

class ImmInt(Token):
	def __init__(self, _value, _size):
		super().__init__(_value, _size)
	
	rules = [[ValidImm]]

class VarData(Token):
	def __init__(self, _value, _size):
		super().__init__(_value, _size)
	
	rules = [[ValidVariable], [ValidDataPtr]]
	
class Label(Token):
	def __init__(self, _value, _size):
		super().__init__(_value, _size)
	
	rules = [[ValidLabel], [ValidInsPtr]]
