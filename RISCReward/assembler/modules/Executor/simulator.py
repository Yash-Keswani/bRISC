import os
import pathlib
import uuid
from enum import Enum

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from .pipeline import Pipeline, LineInfo
from .storage import Registry, Memory
from ..Packaging import template_pb2

CACHE_DIR = str(pathlib.Path(__file__).parent.resolve()) + '/../../cache/'

class Mode(Enum):
	RUN = 0
	DEBUG = 1
	STEP = 2

class Executor:
	# initialise memory and registry
	mem: Memory
	reg: Registry
	size: int = 0
	time: int = 0
	STALLING: bool = False
	BRANCHING: bool = False
	lines: [LineInfo] = []
	
	@classmethod
	def serialise(cls, state: template_pb2.running_state, token: str = None):
		todump = template_pb2.executor()
		todump.size = cls.size
		todump.time = cls.time
		todump.mem.CopyFrom(cls.mem.__serialise__())
		todump.reg.CopyFrom(cls.reg.__serialise__())
		todump.pipeline_usage.CopyFrom(Pipeline.__serialise__())
		todump.state.CopyFrom(state)
		
		if token is None:
			token = str(uuid.uuid4())
		towrite = todump.SerializeToString()
		# towrite = google.protobuf.text_format.MessageToString(todump)
		towrite = pad(towrite, AES.block_size)
		
		ENCRYPTION_KEY = os.environ.get("ENCRYPTIONKEY").encode()
		INIT_VECTOR = os.environ.get("INITVECTOR").encode()
		cipher = AES.new(ENCRYPTION_KEY, AES.MODE_CBC, INIT_VECTOR)
		towrite_enc = cipher.encrypt(towrite)
		with open(CACHE_DIR + token, "wb+") as fl:
			fl.write(towrite_enc)
		
		return token
	
	# print(dump_dict)
	
	@classmethod
	def deserialise(cls, token: str):
		torestore = template_pb2.executor()
		ENCRYPTION_KEY = os.environ.get("ENCRYPTIONKEY").encode()
		INIT_VECTOR = os.environ.get("INITVECTOR").encode()
		cipher = AES.new(ENCRYPTION_KEY, AES.MODE_CBC, INIT_VECTOR)
		with open(CACHE_DIR + token, "rb") as fl:
			parse_me = unpad(cipher.decrypt(fl.read()), AES.block_size)
		torestore.ParseFromString(parse_me)
		
		cls.size = torestore.size
		cls.time = torestore.time
		cls.state = torestore.state
		
		cls.mem.__deserialise__(torestore.mem)
		cls.reg.__deserialise__(torestore.reg)
		Pipeline.__deserialise__(torestore.pipeline_usage)
		
		toretlines = [LineInfo() for x in range(5)]
		for i, j in zip(toretlines, torestore.state.lines):
			i.__deserialise__(j)
		return torestore.state.BRANCHING, torestore.state.STALLING, toretlines
	
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
	def restore_state(cls, reg, mem, code, time, size):
		cls.mem = mem
		cls.reg = reg
		cls.code = code
		cls.time = time
		cls.size = size
	
	@classmethod
	def process(cls, pipelined=False, token: str = None, action: Mode = Mode.RUN):
		toret = {
			"reg_dump": "",  # info in all registers as an instruction leaves the processor
			"mem_dump": "",  # info in memory at end of execution
			"state_dump": "",  # info of each line as it leaves the processor
			"pipeline": "",  # lines in the pipeline in each clock cycle
		}
		
		if token is not None and action is Mode.STEP:
			BRANCHING, STALLING, lineobj = cls.deserialise(token)
		else:
			lineobj = [LineInfo() for _ in range(5)]
			STALLING: bool = False
			BRANCHING: bool = False
		
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
				
				cls.reg.PC += 1
				Pipeline.set_next_get_branching(curr_line)
				
				toret["reg_dump"] += f"{curr_line.lno:08b} {cls.reg.fetch_reg()}"
				toret["state_dump"] += curr_line.__str__()
			toret["mem_dump"] = cls.mem.fetch_mem()
			toret["pipeline"] = Pipeline.getUsage()
			return toret
		
		else:
			while cls.reg.PC < cls.size or any((not lineobj[x].empty() for x in range(5))) or cls.reg.PC == 0:
				lineobj.pop()
				if not STALLING:
					lineobj.insert(0, LineInfo())  # put new line in F to read
				else:
					lineobj.insert(2, LineInfo())  # put stall bubble in X
				
				if cls.reg.PC < cls.size:  # there are lines in the memory to read
					lineobj[0].line_text = f'{cls.mem.read_loc(cls.reg.PC):016b}'
				else:  # there are no lines to read
					lineobj[0].line_text = ""
				
				Pipeline.usage.append([])
				cls.time += 1
				lineobj[0].lno = cls.reg.PC
				
				Pipeline.F(lineobj[0])
				Pipeline.D(lineobj[1])
				
				STALLING = cls.reg.STALLING() or cls.mem.STALLING()
				if not lineobj[0].empty() and not STALLING:
					cls.reg.PC = lineobj[0].lno + 1  # Branching Speculation!
					
				Pipeline.X(lineobj[2])
				BRANCHING = Pipeline.set_next_get_branching(lineobj[2])
				
				Pipeline.M(lineobj[3])
				Pipeline.W(lineobj[4])

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
					STALLING = False

				if not lineobj[4].empty():
					toret["reg_dump"] += f"{lineobj[4].lno:08b} {cls.reg.fetch_reg()}"
					toret["state_dump"] += lineobj[4].__str__()
				
				if action is Mode.STEP or action is Mode.DEBUG:
					break
			
			state = template_pb2.running_state()
			state.STALLING = STALLING
			state.BRANCHING = BRANCHING
			for x in lineobj:
				state.lines.add().CopyFrom(x.__serialise__())
			
			if token is None:
				token = cls.serialise(state)
			else:
				cls.serialise(state, token)
			
			toret["mem_dump"] = cls.mem.fetch_mem()
			toret["pipeline"] = Pipeline.getUsage()
			toret["state"] = lineobj
			toret["regs"] = cls.reg.fetch_reg()
			toret["token"] = token
			return toret
