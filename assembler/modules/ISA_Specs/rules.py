from __future__ import annotations  # 3.9 Compatibility Hack
from abc import ABC, abstractmethod
from .imports import CONF, ErrorLogger, MockMemory

class Rule(ABC):
	__slots__ = []
	
	def __bool__(self):
		return self.check
	
	@staticmethod
	@abstractmethod
	def check(*args, **kwargs) -> tuple[bool, str]:
		raise NotImplementedError

class ValidRegister(Rule):
	@staticmethod
	def check(value: str) -> tuple[bool, str]:
		pre: str = CONF.conf.instruction.prefixes.register
		pre2: str = CONF.conf.registry.flags.name
		if not (value.startswith(pre) or value.startswith(pre2)):
			ErrorLogger.buf_log(f"Invalid prefix for general register. Use {pre} instead.")
			return False, value
		return True, value.lstrip(pre)

class ValidGeneralRegister(Rule):
	@staticmethod
	def check(value: str) -> tuple[bool, str]:
		pre: str = CONF.conf.instruction.prefixes.register
		reg_name = value.lstrip(pre)
		if not reg_name.isnumeric():
			ErrorLogger.log(f"Register name {pre}{reg_name} is not numeric.")
			return False, value
		if not 0 <= int(reg_name) < CONF.conf.registry.general:
			ErrorLogger.log(f"Register value {reg_name} is out of bounds.")
			return False, value
		return True, reg_name

class ValidSpecialRegister(Rule):
	@staticmethod
	def check(value: str) -> tuple[bool, str]:
		pre: str = CONF.conf.instruction.prefixes.register
		reg_name = value.lstrip(pre)
		if reg_name not in CONF.conf.registry.special.to_dict():
			ErrorLogger.log(f"Register name {pre}{reg_name} is not defined.")
			return False, value
		return True, str(CONF.conf.registry.special[reg_name])
	
class ValidFlagsRegister(Rule):
	@staticmethod
	def check(value: str) -> tuple[bool, str]:
		if not (value == CONF.conf.registry.flags.name):
			ErrorLogger.log(f"Invalid FLAGS register. Use {CONF.conf.registry.flags} instead.")
			return False, value
		return True, CONF.conf.registry.flags.value

class ValidInsPtr(Rule):
	@staticmethod
	def check(value: int) -> tuple[bool, int]:
		if not CONF.conf.memory.ins_space[0] <= value <= CONF.conf.memory.ins_space[1]:
			ErrorLogger.log(f"Memory address {value} is not within the instruction space.")
			return False, value
		return True, value

class ValidDataPtr(Rule):
	@staticmethod
	def check(value: int) -> tuple[bool, int]:
		if not CONF.conf.memory.data_space[0] <= value <= CONF.conf.memory.data_space[1]:
			ErrorLogger.log(f"Memory address {value} is not within the data space.")
			return False, value
		return True, value

class ValidInstruction(Rule):
	@staticmethod
	def check(value: str) -> tuple[bool, str]:
		if value not in CONF.insts.keys():
			ErrorLogger.log(f"Invalid instruction name {value}")
			return False, value
		return True, value

class ValidVariable(Rule):
	@staticmethod
	def check(value: str) -> tuple[bool, int]:
		if not MockMemory.has_var(value):
			ErrorLogger.log(f"Invalid variable name {value}")
			return False, -1
		return True, MockMemory.var_addr(value)
	
class ValidLabel(Rule):
	@staticmethod
	def check(value: str) -> tuple[bool, int]:
		if not MockMemory.has_label(value):
			ErrorLogger.log(f"Invalid variable name {value}")
			return False, -1
		return True, MockMemory.label_addr(value)
	
class ValidImm(Rule):
	@staticmethod
	def check(value: str) -> tuple[bool, int]:
		pre = CONF.conf.instruction.prefixes.immediate
		if not value.startswith(pre):
			ErrorLogger.log(f"Invalid Immediate, please use prefix {pre}")
			return False, -1
		if not value.lstrip(pre).isnumeric():
			ErrorLogger.log(f"Immediate value must be numeric")
			return False, -1
		return True, int(value.lstrip(pre))
