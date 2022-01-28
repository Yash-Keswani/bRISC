import os

from .errors import Logger, check_cat, check_variant, Error
from .reader import find_cat, find_variant, encode
from .memory import Memory

def parse(text: str) -> tuple[list[int], str] | str:
	err = Logger()
	commands: list[str] = []
	fl: list[str] = text.split('\n')

	# only include instructions in line count
	ins_cnt = len([x for x in fl if x.strip() != '' and not x.strip().startswith('var')])
	line_cnt = len(fl)

	mem = Memory(ins_cnt)

	# FIRST PASS - SETS VARIABLES
	insts = 0
	for PC, line in enumerate(fl):
		line = line.strip()
		
		variant = find_variant(line)
		error = check_variant(variant, line, PC, False)
		
		if error[0] or variant =='blank':
			continue
		
		elif variant == 'label':  # will always be followed by instruction
			mem.store_label(line.split(':')[0], insts)
			insts += 1
		
		elif variant == 'variable':
			mem.store_var(line[4:])  # excluding 'var '
		
		else:
			insts += 1

	# SECOND PASS
	sourcemap: list[int] = []
	for PC, line in enumerate(fl):
		line = line.strip()
	
		if (any((x.strip() != '' for x in fl[PC+1:])) and line.endswith('hlt')):
			err.log_errors(PC, [Error('hlt present before end of code', PC)])
		if (PC >= line_cnt):
			if (not line.endswith('hlt')):
				err.log_errors(PC + 1, [Error('hlt not present at end of code', PC)])
		
		variant = find_variant(line)
		error = check_variant(variant, line, PC, len(sourcemap) > 0)
		
		if variant == 'label':
			# Turns label into instruction 'labelname: add R0 R1 R2' => 'add R0 R1 R2'
			line = line.split(':')[1].lstrip()
			variant = find_variant(line)
			check_variant(variant, line, PC, len(sourcemap) > 0)
		
		if error[0]:  # variant error handling
			err.log_errors(PC + 1, error[1])
			continue  # stop processing the line here, go to the next line
		
		if variant == 'blank' or variant == 'variable':
			continue
		
		if variant == 'instruction':
			opc, cat = find_cat(line)['opcode'], find_cat(line)['cat']
			error = check_cat(opc, cat, line, mem, PC)
			
			# handles instruction category-specific errors
			if error[0]:
				err.log_errors(PC + 1, error[1])
				continue
			
			buffer = encode(opc, cat, line, mem)
			sourcemap.append(PC)
			commands.append(buffer)

	if err.errors_present():
		return [-1], '\n'.join(err.get_errors())
	else:
		if os.environ.get("TESTING") == '1':
			return '\n'.join(commands)
		else:
			return sourcemap, '\n'.join(commands)
	