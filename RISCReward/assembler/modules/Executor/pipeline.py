from dataclasses import dataclass

from .controller import CU
from .logic import LU
from .storage import Registry, Memory
from ..Packaging import template_pb2

def copy_dict(dict1: dict[any], dict2: dict[any]):
	for key, value in dict2.items():
		dict1[key] = value

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
	lno: int = -1
	line_text: str = ""
	srcs: list[int] = None
	dests: list[int] = None
	out: dict[str, any] = None
	opc: int = -1
	cat: str = ""
	
	def __init__(self):
		self.lno = self.opc = -1
		self.cat = ""
		self.srcs = []
		self.dests = []
		self.out = {"main": -1, "alter": -1, "branch": -1, "flags": -1}
	
	def __serialise__(self) -> template_pb2.line_info:
		toret = template_pb2.line_info()
		toret.lno = self.lno
		toret.line_text = self.line_text
		toret.srcs.extend(self.srcs)
		toret.dests.extend(self.dests)
		copy_dict(toret.out, self.out)
		toret.opc = self.opc
		toret.cat = self.cat
		return toret
	
	def __deserialise__(self, data: template_pb2.line_info):
		self.lno = data.lno
		self.line_text = data.line_text
		self.srcs = list(data.srcs)
		self.dests = list(data.dests)
		self.out = dict(data.out)
		self.opc = data.opc
		self.cat = data.cat
	
	def empty(self) -> bool:
		return self.line_text == ""

class Pipeline:
	mem: Memory
	reg: Registry
	usage: list[list[int]]
	
	def __init__(self, mem: Memory, reg: Registry):
		Pipeline.mem = mem
		Pipeline.reg = reg
		Pipeline.usage = []
	
	@classmethod
	def __serialise__(cls) -> template_pb2.pipeline:
		toret = template_pb2.pipeline()
		for row in cls.usage:
			curr = toret.lines.add()
			curr.reg_num.extend(row)
		return toret
	
	@classmethod
	def __deserialise__(cls, data: template_pb2.pipeline):
		for row in data.lines:
			cls.usage.append(list(row.reg_num))
	
	@classmethod
	def getUsage(cls):
		return cls.usage
	
	@classmethod
	def setUsage(cls, usage):
		cls.usage = usage
	
	@classmethod
	@returnIfNone
	def F(cls, line: LineInfo):
		line.opc, line.cat = CU.interpret(line.line_text)
	
	@classmethod
	@returnIfNone
	def D(cls, line: LineInfo):
		line.srcs = CU.fetch_sources(line.opc, line.cat, line.line_text, cls.mem, cls.reg)
		
		if -1 in line.srcs:  # prevents circular dependency by locking one's one source in an intermediate stage
			return
		
		line.dests = CU.fetch_destinations(line.opc, line.cat, line.line_text)
		
		for dest in line.dests:
			if dest < 0:
				continue
			if dest <= 7:
				cls.reg.hold(dest)
			else:
				cls.mem.hold(dest)
		
		if line.opc == 0b01110 or line.cat == 'A':  # overflow is a bitch
			cls.reg.hold(7)
	
	@classmethod
	@returnIfNone
	def X(cls, line: LineInfo) -> None:
		line.out = LU.call(line.opc, line.srcs)
	
	@classmethod
	def set_next_get_branching(cls, line: LineInfo):
		if line.empty():
			return False
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
			if 0 <= dest <= 7:
				cls.reg.release(dest)
			if line.opc == 0b01110 or line.cat == 'A':  # overflow is a bitch
				cls.reg.release(7)  # FLAGS
