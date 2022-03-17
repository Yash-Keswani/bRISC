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
		toret = {
			"reg_dump": "",    # info in all registers as an instruction leaves the processor
			"mem_dump": "",    # info in memory at end of execution
			"state_dump": "",  # info of each line as it leaves the processor
			"pipeline": "",    # lines in the pipeline in each clock cycle
		}
		
		if not pipelined:
			while cls.reg.PC < cls.size:
				curr_line = LineInfo()
				curr_line.line_text = f'{cls.mem.read_loc(cls.reg.PC):016b}'
				curr_line.lno = cls.reg.PC

				Pipeline.usage.append([])
				cls.time += 1
				
				Pipeline.F(curr_line)
				Pipeline.D(curr_line)
				Pipeline.X(curr_line)
				Pipeline.M(curr_line)
				Pipeline.W(curr_line)
			
				toret["reg_dump"] += f"{curr_line.lno:08b} {cls.reg.fetch_reg()}"
				toret["state_dump"] += curr_line.__str__()
			toret["mem_dump"] = cls.mem.fetch_mem()
			toret["pipeline"] = Pipeline.getUsage()
			return toret
		
		else:
			lineobj = [LineInfo() for _ in range(5)]
			STALLING: bool
			BRANCHING: bool
			
			while cls.reg.PC < cls.size or any((not lineobj[x].empty() for x in range(5))) or cls.reg.PC == 0:
				if cls.reg.PC < cls.size:  # there are lines in the memory to read
					lineobj[0].line_text = f'{cls.mem.read_loc(cls.reg.PC):016b}'
				else:  # there are no lines to read
					lineobj[0].line_text = None
			
				Pipeline.usage.append([])
				cls.time += 1
				lineobj[0].lno = cls.reg.PC
				
				Pipeline.F(lineobj[0])
				Pipeline.M(lineobj[3])
				Pipeline.W(lineobj[4])
				Pipeline.D(lineobj[1])
				
				STALLING = cls.reg.STALLING() or cls.mem.STALLING()
				if not lineobj[0].empty() and not STALLING:
					cls.reg.PC = lineobj[0].lno + 1  # Branching Speculation!
					
				BRANCHING = Pipeline.X(lineobj[2])
				
				if BRANCHING:  # Free all locks held by purged lines
					for loc in set(lineobj[0].dests) | set(lineobj[1].dests):
						if loc < 0:
							continue
						if loc <= 7:
							cls.reg.release(loc)
						else:
							cls.mem.release(loc)
					
					for i in lineobj[0:2]:
						if i.opc == 0b01110 or i.cat == 'A':  # free implicit lock held on flags register
							cls.reg.release(7)
							
					lineobj[0] = lineobj[1] = LineInfo()  # purge lines in F and D
					
				if not lineobj[4].empty():
					toret["reg_dump"] += f"{lineobj[4].lno:08b} {cls.reg.fetch_reg()}"
					toret["state_dump"] += lineobj[4].__str__()
					
				lineobj.pop()
				if not STALLING:
					lineobj.insert(0, LineInfo())  # put new line in F to read
				else:
					lineobj.insert(2, LineInfo())  # put stall bubble in X
		
			toret["mem_dump"] = cls.mem.fetch_mem()
			toret["pipeline"] = Pipeline.getUsage()
			return toret
	