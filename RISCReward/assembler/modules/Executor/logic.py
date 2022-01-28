class LU:
	# adds two integers
	@staticmethod
	def add(params: list[int]):
		return {
			'main': (params[0] + params[1]) % 65536,
			'flags': int(f"{int(params[0] + params[1] >= 65536)}000", base=2)
		}
		
	# subtracts two integers
	@staticmethod
	def sub(params: list[int]):
		return {
			'main': max(params[0] - params[1], 0),
			'flags': int(f"{int(params[0] - params[1] < 0)}000", base=2)
		}
		
	# multiply two integers
	@staticmethod
	def mul(params: list[int]):
		return {
			'main': (params[0] * params[1]) % 65536,
			'flags': int(f"{int(params[0] * params[1] >= 65536)}000", base=2)
		}
		
	# divides two integers
	@staticmethod
	def div(params: list[int]):
		return {
			'main': params[0] // params[1],
			'alter': params[0] % params[1]
		}
		
	# performs bitwise XOR operation
	@staticmethod
	def xor(params: list[int]):
		return {
			'main': params[0] ^ params[1],
		}
		
	# performs bitwise OR operation
	@staticmethod
	def orr(params: list[int]):
		return {
			'main': params[0] | params[1],
		}
		
	# performs bitwise AND operation
	@staticmethod
	def andr(params: list[int]):
		return {
			'main': params[0] & params[1],
		}
		
	# performs bitwise NOT operation
	@staticmethod
	def notr(params: list[int]):
		return {
			"main": ~ params[1] + 2**16
		}
		
	# compares two integers
	@staticmethod
	def cmp(params: list[int]):
		return {
			'flags': int(
				f"0{int(params[0] < params[1])}{int(params[0] > params[1])}{int(params[0] == params[1])}", base=2
			)
		}
		
	# move from register to register
	@staticmethod
	def movr(params: list[int]):
		return {
			'main': params[1]
		}
		
	# load from memory to register
	@staticmethod
	def ld(params: list[int]):
		return {
			'main': params[1]
		}
		
	# store register in memory
	@staticmethod
	def st(params: list[int]):
		return {
			'main': params[0]
		}
		
	# move immediate to register
	@staticmethod
	def movi(params: list[int]):
		return {
			'main': params[1]
		}
		
	# jumps to memory address
	@staticmethod
	def jmp(params: list[int]):
		return {
			'main': params[0],
			'branch': 1
		}
		
	# jumps to memory address if the greater than flag is set
	@staticmethod
	def jgt(params: list[int]):
		return {
			'main': params[0],
			'branch': int(f'{params[1]:016b}'[-2])
		}
		
	# jumps to memory address if the less than flag is set
	@staticmethod
	def jlt(params: list[int]):
		return {
			'main': params[0],
			'branch': int(f'{params[1]:016b}'[-3])
		}
		
	# jumps to memory address if the equal flag is set
	@staticmethod
	def je(params: list[int]):
		return {
			'main': params[0],
			'branch': int(f'{params[1]:016b}'[-1])
		}
		
	# right shifts register by an immediate value
	@staticmethod
	def rs(params: list[int]):
		return {
			'main': params[0] >> params[1]
		}
		
	# left shifts register by an immediate value
	@staticmethod
	def ls(params: list[int]):
		return {
			'main': params[0] << params[1]
		}
		
	# stops running code
	@staticmethod
	def hlt(params: list[int]):
		return {}
	
	switcher = {
		0b00000: add,
		0b00001: sub,
		0b00010: movi,
		0b00011: movr,
		0b00100: ld,
		0b00101: st,
		0b00110: mul,
		0b00111: div,
		0b01000: rs,
		0b01001: ls,
		0b01010: xor,
		0b01011: orr,
		0b01100: andr,
		0b01101: notr,
		0b01110: cmp,
		0b01111: jmp,
		0b10000: jlt,
		0b10001: jgt,
		0b10010: je,
		0b10011: hlt,
	}
	
	@classmethod
	def call(cls, opc: int, params: list) -> dict:
		"""
		calls the function for the given opcode and parameters.

		all parameters are integers in raw [base 10] form.

		note the purposes of the output values:
			- main value will contain the main output, which will be stored in a registry.
			- alter value will contain either a second output value [only for div instruction].
			- branch value will contain whether or not to follow branch instruction.
			- flags value will contain the new value of the last 4 bits in the FLAGS register.

		it is to be noted that the alter, branch, and flags values can be merged into one; but they are kept separate for clearer documentation.
		"""
		toret = {
			'main': 0,
			'alter': 0,
			'branch': 0,
			'flags': 0,
		}
		
		gotten = cls.switcher[opc](params)
		
		for x in gotten:
			toret[x] = gotten[x]
		
		return toret
