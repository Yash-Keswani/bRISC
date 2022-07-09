from __future__ import annotations  # 3.9 Compatibility Hack
import os
from ..ISA_Specs.base import ISA
from ..ISA_Specs.imports import MockMemory as Memory, CONF, ErrorLogger, Variant
from ..ISA_Specs.FancyRISC import ISA_FancyRISC

def parse(text: str) -> tuple[list[int], str] | str:
	if CONF.IMPORTED_ISA != "FancyRISC":
		CONF.reload("FancyRISC")
	isa: ISA = ISA_FancyRISC()
	err = ErrorLogger
	commands: list[str] = []
	
	# remove comments
	fl: list[str] = [x.partition('#')[0] for x in text.split('\n')]
	
	# only include instructions in line count
	ins_cnt = len([x for x in fl if x.strip() != '' and not x.strip().startswith('var')])
	line_cnt = len(fl)
	
	Memory.load(ins_cnt)
	
	# FIRST PASS - SETS VARIABLES
	insts = 0
	for lno, line in enumerate(fl):
		ErrorLogger.tick()
		line = line.strip()
		
		variant = isa.find_variant(line)
		error = isa.check_variant(variant, line, False)
		
		if error:
			continue
		
		if variant == Variant.lab:  # may not always be followed by instruction
			Memory.store_label(line.split(':')[0], insts)
			variant = isa.find_variant(line)
			error = isa.check_variant(variant, line, False)
			
		if error or variant == Variant.blank:
			continue
		
		elif variant == Variant.var:
			Memory.store_var(line[4:])  # excluding 'var '
		
		else:
			insts += 1
	
	# SECOND PASS
	sourcemap: list[int] = []
	for lno, line in enumerate(fl):
		line = line.strip()
		
		if (any((x.strip() != '' for x in fl[lno + 1:])) and line.endswith('hlt')):
			err.log('hlt present before end of code')
		if (lno >= line_cnt):
			if (not line.endswith('hlt')):
				err.log('hlt not present at end of code')
		
		variant = isa.find_variant(line)
		error = isa.check_variant(variant, line, len(sourcemap) > 0)
		
		if variant == Variant.lab:
			# Turns label into instruction 'labelname: add R0 R1 R2' => 'add R0 R1 R2'
			line = line.split(':')[1].lstrip()
			variant = isa.find_variant(line)
			isa.check_variant(variant, line, len(sourcemap) > 0)
		
		if error:  # variant error handling
			continue  # stop processing the line here, go to the next line
		
		if variant == Variant.blank or variant == Variant.var:
			continue
		
		if variant == Variant.ins:
			tokens = isa.tokenise(line)
			sourcemap.append(lno)
			commands.append(isa.encode(tokens))
	
	errors = ErrorLogger.get_err()
	if any(len(x) > 0 for x in errors):
		return [-1], str(errors)
	else:
		if os.environ.get("TESTING") == '1':
			return '\n'.join(commands)
		else:
			return sourcemap, '\n'.join(commands)
