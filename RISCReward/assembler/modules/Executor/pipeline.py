from dataclasses import dataclass

from .controller import CU
from .logic import LU
from .storage import Registry, Memory

def returnIfNone(fun):
	def wrap(cls, line):
		if line.empty():
			return
		else:
			return fun(cls, line)
	return wrap

@dataclass
class LineInfo():
	lno: int = None
	line_text: str = None
	srcs: list[int] = None
	dests: list[int] = None
	out: dict[str, int | bool] = None
	opc: int = None
	cat: str = None
	
	def empty(self) -> bool:
		return self.line_text is None

class Pipeline:
	mem: Memory
	reg: Registry
	
	def __init__(self, mem: Memory, reg: Registry):
		Pipeline.mem = mem
		Pipeline.reg = reg
	
	@classmethod
	@returnIfNone
	def F(cls, line: LineInfo):
		line.lno = cls.reg.PC
		line.opc, line.cat = CU.interpret(line.line_text)
	
	@classmethod
	@returnIfNone
	def D(cls, line: LineInfo):
		line.srcs = CU.fetch_sources(line.cat, line.line_text, cls.mem, cls.reg)
		
		if -1 in line.srcs:  # prevents circular dependency by locking one's one source in an intermediate stage
			return
		
		line.dests = CU.fetch_destinations(line.opc, line.cat, line.line_text, cls.reg)
	
	@classmethod
	@returnIfNone
	def X(cls, line: LineInfo) -> bool:
		line.out = LU.call(line.opc, line.srcs)
		return CU.next_instruction(line.out, cls.reg)
	
	@classmethod
	@returnIfNone
	def M(cls, line: LineInfo):
		CU.store_results_mem(line.dests, line.out, line.opc, line.cat, cls.mem)
	
	@classmethod
	@returnIfNone
	def W(cls, line: LineInfo):
		CU.store_results_reg(line.dests, line.out, line.opc, line.cat, cls.reg)
		