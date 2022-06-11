from abc import ABC, abstractmethod
from .imports import conf, opcodes, insts

class Rule(ABC):
	def __bool__(self):
		return self.check
	
	@abstractmethod
	def check(self, *args, **kwargs) -> bool:
		raise NotImplementedError

class ValidGeneralRegister(Rule):
	def check(self, value: str) -> bool:
		pre: str = conf.instruction.prefix
		return value.startswith(pre) and 0 <= int(value.lstrip(pre)) < conf.registry.general

class ValidSpecialRegister(Rule):
	def check(self, value: str) -> bool:
		pre: str = conf.instruction.prefix
		return value.startswith(pre) and (value.lstrip(pre)) in conf.registry.special
	
class ValidFlagsRegister(Rule):
	def check(self, value: str) -> bool:
		return value == conf.registry.flags

class ValidHeapMemoryAddress(Rule):
	def check(self, value: int) -> bool:
		return conf.memory.ins_space[0] < value < conf.memory.ins_space[1]
	
class ValidOpcode(Rule):
	def check(self, value: int) -> bool:
		return value in opcodes