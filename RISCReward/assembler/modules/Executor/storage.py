from ..Packaging import template_pb2

def copy_dict(dict1: dict[any], dict2: dict[any]):
	for key, value in dict2.items():
		dict1[key] = value

class Locker:
	def __init__(self):
		self.locks = {}
		self.waiting = {}
		
	def __serialise__(self)->template_pb2.locker:
		toret = template_pb2.locker()
		copy_dict(toret.locks, self.locks)
		copy_dict(toret.waiting, self.waiting)
		return toret
	
	# stall if any needed resource is locked
	def STALLING(self) -> bool:
		return any((self.waiting[x] for x in self.waiting))
	
	# holds a lock on a register
	def hold(self, loc: int) -> None:
		if self.locks.get(loc):
			self.locks[loc] += 1
		else:
			self.locks[loc] = 1
	
	# checks if a location is locked - if the location isnt present in the lock table, it returns false
	def check(self, loc: int) -> bool:
		if toret := self.locks.get(loc) and self.locks[loc] > 0:
			self.waiting[loc] = True
		return toret
	
	# releases the lock on a register
	def release(self, loc: int) -> None:
		if self.locks[loc] > 0:
			self.locks[loc] -= 1
		if self.locks[loc] == 0:
			self.waiting[loc] = False

class Registry(Locker):
	# initialises register set which is used by the simulator
	def __init__(self):
		super().__init__()
		self.PC = 0b0000_0000
		self.FLAGS = 0b0000_0000_0000_0000  # will be removed
		self.regs = [0b0000_0000_0000_0000] * 7  # general purpose registers
		self.sregs: dict[str | int] = {  # will take its place
			"RSL": 0b0000_0000_0000_0000,
			"RSS": 0b0000_0000_0000_0000,
			"RSC": 0b0000_0000_0000_0000,
			"RSF": 0b0000_0000_0000_0000,
			"RSN": 0b0000_0000_0000_0000,
			"RSR": 0b0000_0000_0000_0000,
			"RSA": 0b0000_0000_0000_0000,
			"RSX": 0b0000_0000_0000_0000
		}
		self.locks = {X: 0 for X in range(8)}  # locked registers cannot be written into
		self.waiting = {X: False for X in range(8)}  # locked registers cannot be written into
		
	def __serialise__(self)->template_pb2.registry:
		toret = template_pb2.registry()
		toret.PC = self.PC
		toret.FLAGS = self.FLAGS
		toret.regs.extend(self.regs)
		copy_dict(toret.sregs, self.sregs)
		toret.all_locks.CopyFrom(super().__serialise__())
		return toret
	
	def __deserialise__(self, data: template_pb2.registry):
		self.PC = data.PC
		self.FLAGS = data.FLAGS
		self.regs = list(data.regs)
		self.sregs = data.sregs
		self.locks = data.all_locks.locks
		self.waiting = data.all_locks.waiting
		
	# writes a value to a certain register
	def write_reg(self, loc: int, val: int) -> None:
		self.regs[loc] = val
	
	# reads a value from a certain register
	def read_reg(self, loc: int) -> int:
		if self.check(loc):
			return -1
		if loc == 7:
			return self.FLAGS
		return self.regs[loc]
	
	# sets the flags register with the given flags
	def set_flags(self, flags: str) -> None:
		self.FLAGS = flags
	
	# gets program counter in a printable format
	def fetch_PC(self) -> str:
		return f"{self.PC:08b} "
	
	# branches to a named instruction
	def branch_to(self, loc: int) -> None:
		Tracer.log_endline(loc)
		self.PC = loc
	
	# returns the full data within the registry, including flags
	def fetch_reg(self) -> str:
		return " ".join([f'{x:016b}' for x in (self.regs + [self.FLAGS])])+" \n"

class Memory(Locker):
	# initialises memory of the given size
	def __init__(self, size: int):
		super().__init__()
		self.mem = [0b0000_0000_0000_0000] * size
		
	def __serialise__(self) -> template_pb2.memory:
		toret = template_pb2.memory()
		toret.all_locks.CopyFrom(super().__serialise__())
		toret.mem_value.extend(self.mem)
		return toret
	
	def __deserialise__(self, data: template_pb2.memory) -> None:
		self.locks = data.all_locks.locks
		self.mem = data.mem_value
		
	# writes a value at a given memory location
	def write_loc(self, loc: int, val: int) -> None:
		Tracer.log_write(loc)
		self.mem[loc] = val
		
	# reads the value at a given memory location
	def read_loc(self, loc: int) -> int:
		if self.check(loc):
			return -1
		Tracer.log_read(loc)
		return self.mem[loc]
		
	# returns the full data within the memory
	def fetch_mem(self) -> str:
		return "\n".join([f'{x:016b}' for x in self.mem])
	
# logs memory access traces
class Tracer:
	traces: list[tuple[str, int]] = []
	
	# marks that a memory location was read from
	@staticmethod
	def log_read(loc: int) -> None:
		Tracer.traces.append(('R', loc))
	
	# marks that a memory location was written to
	@staticmethod
	def log_write(loc: int) -> None:
		Tracer.traces.append(('W', loc))
	
	# marks the end of the line
	@staticmethod
	def log_endline(loc: int) -> None:
		Tracer.traces.append(('E', loc))
	
	@staticmethod
	def get_all_traces():
		traces_read_x = []
		traces_read_y = []
		traces_write_x = []
		traces_write_y = []
		
		l = 0
		for x in Tracer.traces:
			if x[0] == 'R':
				traces_read_x.append(l)
				traces_read_y.append(x[1])
			elif x[0] == 'W':
				traces_write_x.append(l)
				traces_write_y.append(x[1])
			else:
				l += 1
		
		return {'x': {'read': traces_read_x, 'write': traces_write_x},
		        'y': {'read': traces_read_y, 'write': traces_write_y}}
