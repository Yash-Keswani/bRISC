### Registers
There is a total of 16 supported registers. Out of these, 8 are general-purpose registers, and the remaining 8 are special-purpose. All registers are 2 bytes in size

#### General Purpose Registers
-> 8 in quantity
-> Can be read from and written into
-> Format is `R[0:8]`
-> Load / Store operations can only be performed from these registers

### Special Purpose Registers
-> 8 in quantity
-> Can only be read from
-> Load / Store operations cannot be performed from these registers
-> Register specifications are as follows:
	-> `RSL` - link register. Stores the destination that return into
	-> `RSS` - stack pointer. Stores the top of the call stack
	-> `RSC` - custom stack pointer. Stores the top of the user stack
	-> `RSF` - has FLAGS as an alias. Stores information from compare instructions
	-> `RSN` - anomaly register. Stores information on overflow and underflow
	-> `RSR` - return register. Stores the value returned by any function
	-> `RSA` - alternate return register. Stores a second possible value returned by a function. Use this to refer to a memory location if 3+ values are to be returned
	-> `RSX` - currently unused

### Calling Convention
-> R0, R1, R2, R3 are `caller-preserved`
-> R4, R5, R6, R7 are `callee-preserved`
-> Parameters should be sent through R0, R1, R4, and R5, in that order
-> Special-purpose registers should be assumed to be always clobbered

### Transfer Instructions
[TODO: hyperlinks here]
-> `movi` puts an immediate value into a register
-> `movr` puts the value of a general-purpose register into another general-purpose register
-> `movs` puts the value of a special-purpose register into a general-purpose register

## Memory
The memory has a size of 512 bytes, of which the first 128 are allocated for instructions. 
-> Instruction memory cannot be written or read into by load / store
-> Likewise, an instruction cannot be read from outside the instruction memory, through a jump
-> The memory is two-byte-addressable. Each instruction and register value is two bytes as well