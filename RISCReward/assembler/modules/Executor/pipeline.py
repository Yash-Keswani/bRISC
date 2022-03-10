from dataclasses import dataclass

from .controller import CU
from .logic import LU
from .storage import Registry, Memory

def returnIfNone(fun):
	def wrap(cls, line, **kwargs):
		if line.empty():
			cls.usage[-1].append(-1)
			return
		else:
			cls.usage[-1].append(line.lno)
			return fun(cls, line, **kwargs)
	return wrap

@dataclass
class LineInfo():
	last_index: int = 0
	
	lno: int = None
	line_text: str = None
	srcs: list[int] = None
	dests: list[int] = None
	out: dict[str, int | bool] = None
	opc: int = None
	cat: str = None
	locks: list[int] = None  # locks that this line is waiting to be released
	
	def __init__(self):
		self.dests = []
		self.locks = []
	
	def empty(self) -> bool:
		return self.line_text is None

class Pipeline:
	mem: Memory
	reg: Registry
	usage: list[list[int]]
	
	def __init__(self, mem: Memory, reg: Registry):
		Pipeline.mem = mem
		Pipeline.reg = reg
		Pipeline.usage = []
		
	@classmethod
	def getUsage(cls):
		return cls.usage
	
	@classmethod
	@returnIfNone
	def F(cls, line: LineInfo):
		line.opc, line.cat = CU.interpret(line.line_text)
	
	@classmethod
	@returnIfNone
	def D(cls, line: LineInfo):
		cls.__D(line)
		
	@classmethod
	def __D(cls, line: LineInfo):
		line.srcs = CU.fetch_sources(line.cat, line.line_text, cls.mem, cls.reg)
		
		if -1 in line.srcs:  # prevents circular dependency by locking one's one source in an intermediate stage
			return
		
		line.dests = CU.fetch_destinations(line.opc, line.cat, line.line_text)
		
		for dest in line.dests:
			if dest <= 7:
				cls.reg.hold(dest)
			else:
				cls.mem.hold(dest)
		
		if line.opc == 0b01110 or line.cat == 'A':  # overflow is a bitch
			cls.reg.hold(7)  # FLAGS
	
	@classmethod
	@returnIfNone
	def X(cls, line: LineInfo) -> bool:
		line.out = LU.call(line.opc, line.srcs)
		return CU.next_instruction(line.out, cls.reg)
	
	@classmethod
	@returnIfNone
	def M(cls, line: LineInfo):
		CU.store_results_mem(line.dests, line.out, line.opc, line.cat, cls.mem)
		
		for dest in line.dests:
			if dest > 7:
				cls.mem.release(dest)
	
	@classmethod
	@returnIfNone
	def W(cls, line: LineInfo):
		CU.store_results_reg(line.dests, line.out, line.opc, line.cat, cls.reg)
		
		for dest in line.dests:
			if dest <= 7:
				cls.reg.release(dest)
			if line.opc == 0b01110 or line.cat == 'A':  # overflow is a bitch
				cls.reg.release(7)  # FLAGS