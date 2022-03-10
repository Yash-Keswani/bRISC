import os

from .pipeline import Pipeline, LineInfo
from .storage import Registry, Memory

class Executor:
	# initialise memory and registry
	mem: Memory
	reg: Registry
	size: int
	time: int = 0
	
	@classmethod
	def load_code(cls, text: str):
		cls.mem = Memory(256)
		cls.reg = Registry()
		cls.size = 0
		cls.time = 0
		Pipeline(cls.mem, cls.reg)
		
		for i, line in enumerate(text.strip().split("\n")):
			cls.mem.write_loc(i, int(line, base=2))
			cls.size += 1

	@classmethod
	def process(cls, pipelined=False):
		toret: str | list[str] = ""
		
		if not pipelined:
			lineobj = [LineInfo()] * 5
		else:
			lineobj = [LineInfo() for _ in range(5)]
		
		STALLING: bool
		BRANCHING: bool
		
		while cls.reg.PC < cls.size or any((not lineobj[x].empty() for x in range(5))) or cls.reg.PC == 0:
			if cls.reg.PC < cls.size:
				lineobj[0].line_text = f'{cls.mem.read_loc(cls.reg.PC):016b}'
			else:
				lineobj[0].line_text = None
		
			Pipeline.usage.append([])
			cls.time += 1
			lineobj[0].lno = cls.reg.PC
			
			Pipeline.F(lineobj[0])
			Pipeline.M(lineobj[3])
			Pipeline.W(lineobj[4])
			Pipeline.D(lineobj[1])
			
			# STALLING = (-1 in lineobj[1].srcs) if not lineobj[1].empty() else False
			STALLING = cls.reg.STALLING() or cls.mem.STALLING()
			
			if not lineobj[0].empty() and not STALLING:
				cls.reg.PC = lineobj[0].lno + 1  # Branching Speculation!
				
			BRANCHING = Pipeline.X(lineobj[2])
			
			if BRANCHING:  # Branching happened
				for loc in set(lineobj[0].dests) | set(lineobj[1].dests):
					if loc <= 7:
						cls.reg.release(loc)
					else:
						cls.mem.release(loc)
				
				for i in lineobj[0:2]:
					if i.opc == 0b01110 or i.cat == 'A':  # overflow is a bitch
						cls.reg.release(7)  # FLAGS
						
				lineobj[0] = lineobj[1] = LineInfo()
			
			#if all((not cls.reg.check(x) for x in lineobj[1].locks)):
			#	STALLING = False
			
			if not lineobj[4].empty():
				if os.environ.get("TESTING") == '1':
					toret += f"{lineobj[4].lno:08b} " + cls.reg.fetch_reg()
				else:
					toret += lineobj[4].__str__()+"\n"
		
			if not pipelined:
				lineobj = [LineInfo()] * 5
			else:
				lineobj.pop()
				lineobj.insert(0 + 2*STALLING, LineInfo())
	
		if os.environ.get("TESTING") == '1':
			toret += cls.mem.fetch_mem()
		else:
			toret = [toret, Pipeline.getUsage()]
		return toret
	