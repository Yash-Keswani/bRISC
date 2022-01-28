class Registry:
	# initialises register set which is used by the simulator
	def __init__(self):
		self.PC = 0b0000_0000
		self.FLAGS = 0b0000_0000_0000_0000
		self.regs = [0b0000_0000_0000_0000] * 7  # general purpose registers
		self.locks = {X: False for X in range(8)}  # locked registers cannot be written into
	
	# holds a lock on a register
	def hold(self, reg: int) -> None:
		self.locks[reg] = True
	
	# checks if a register is locked
	def check(self, reg: int) -> bool:
		return self.locks[reg]
	
	# releases the lock on a register
	def release(self, reg: int) -> None:
		self.locks[reg] = False
	
	# writes a value to a certain register
	def write_reg(self, loc: int, val: int) -> None:
		self.regs[loc] = val
	
	# reads a value from a certain register
	def read_reg(self, loc: int) -> int:
		if self.locks[loc]:
			return -1
		if loc == 7:
			return self.FLAGS
		return self.regs[loc]
	
	# sets the flags register with the given flags
	def set_flags(self, flags: str) -> None:
		self.release(7)
		self.FLAGS = flags
	
	# gets program counter in a printble format
	def fetch_PC(self) -> str:
		return f"{self.PC:08b} "
	
	# branches to a named instruction
	def branch_to(self, loc: int) -> None:
		Tracer.log_endline(loc)
		self.PC = loc
	
	# returns the full data within the registry, including flags
	def fetch_reg(self) -> str:
		return " ".join([f'{x:016b}' for x in (self.regs + [self.FLAGS])])+" \n"

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

class Memory:
	# initialises memory of the given size
	def __init__(self, size: int):
		self.mem = [0b0000_0000_0000_0000] * size
		
	# writes a value at a given memory location
	def write_loc(self, loc: int, val: int) -> None:
		Tracer.log_write(loc)
		self.mem[loc] = val
		
	# reads the value at a given memory location
	def read_loc(self, loc: int) -> int:
		Tracer.log_read(loc)
		return self.mem[loc]
		
	# returns the full data within the memory
	def fetch_mem(self) -> str:
		return "\n".join([f'{x:016b}' for x in self.mem])
