from __future__ import annotations  # 3.9 compatibility hack

from abc import ABC, abstractmethod

from .imports import Variant, Error, ErrorLogger, CONF, MockMemory

from .tokens import RegSrc, RegDest, Inst, Padding, Switcher, Modifier, ImmInt, ImmInsPtr, ImmDataPtr, Token, OpCode, \
	Label, VarData

class ISA(ABC):
	def __init__(self):
		conf = CONF.conf
		self.delimIns = conf.assembler.ins_delimiter
		self.delimParam = conf.assembler.param_delimiter
		self.lineDelim = conf.assembler.line_delimiter
		self.labelPre = conf.assembler.prefixes.label
		self.labelSuf = conf.assembler.suffixes.label
		self.varPrefix = conf.assembler.prefixes.variable
		self.opcodeSize = conf.instruction.opcode_size

	@classmethod
	@abstractmethod
	def check_variant(cls, variant: Variant, line: str, started: bool) -> tuple[bool, list[Error]]:
		pass
	
	def find_variant(self, line: str) -> Variant:
		if line == '':
			return Variant.blank
		elif self.labelSuf in line[1:]:  # TODO: make these regex queries to check for suffixes as well
			return Variant.lab
		elif line.startswith(self.varPrefix):
			return Variant.var
		return Variant.ins
	
	@staticmethod
	def parse_formatters(formatters: dict[str, int]) -> list[(list[Token], int)]:
		fmt_dict = {"reg_s": RegSrc, "reg_d": RegDest, 'imm_ins': ImmInsPtr, 'imm_data': ImmDataPtr, 'imm_int': ImmInt, 'opcode': OpCode, "padding": Padding, "switcher": Switcher, "modifier": Modifier, 'var_data': VarData, 'label': Label}
		fmtrs = []
		for fmt, size in formatters.items():
			fmtrs.append((fmt_dict[fmt.partition('|')[0]], size))
			
		return fmtrs
	
	def tokenise(self, instruction: str) -> list[Token]:
		ins_text, ignored, params_text = instruction.partition(self.delimIns)
		ins = Inst(ins_text, self.opcodeSize)
		params = [ins]
		params.extend([x for x in params_text.split(self.delimParam) if x != ''])
		
		tokens: list[Token] = []
		for opcode, pattern in ins.patterns:
			tokens: list[Token] = []
			params[0] = str(int(opcode[2:], base=2))  # we assume 'opcode' to be the actual opcode and verify this claim
			ErrorLogger.dump()
			
			formatters = self.parse_formatters(pattern['encoding'])
			num_params = sum([1 for x in formatters if not x[0].silent])
			
			if num_params != len(params):
				ErrorLogger.buf_log(f"Invalid number of parameters: {len(params)}")
				continue
			
			i = 0
			for fmtr, size in formatters:
				if fmtr == Padding:
					tokens.append(Padding(0, size))
				elif fmtr == Switcher:
					tokens.append(Switcher(pattern['switcher'], size))
				else:
					tokens.append(fmtr(params[i], size))
					i += 1
					
			if all(token.verify() for token in tokens):
				break
				
		return tokens
	
	def encode(self, tokens: list[Token]) -> str:
		toret = ""
		for token in tokens:
			toret += token.encode()
		return toret
