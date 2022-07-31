from __future__ import annotations  # 3.9 Compatibility Hack
from ..base import Error, ISA
from ..imports import MockMemory as Memory, ErrorLogger
import json
import re

class ISA_SimpleRISC(ISA):
	def check_variant(self, variant: str, line: str, started: bool) -> bool:
		if variant == 'label':
			if line.count(':') >= 2:
				ErrorLogger.log('The ":" symbol cannot be used multiple times in the same line')
				return True
			if line[line.index(':') - 1] == ' ':
				ErrorLogger.log('Label has whitespace before :')
				return True
		elif variant == 'variable':
			if started:
				ErrorLogger.log('Variable defined after start of program')
				return True
		return False
