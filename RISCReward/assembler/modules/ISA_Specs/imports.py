import json
import sys
from pathlib import Path
from typing import IO
from bunch import Bunch

def openp(filepath: str) -> IO:
	return open('assembler/modules/ISA_Specs/FancyRISC/' + filepath)
	# return open(Path(sys.modules[Rule.__module__].__file__).with_name(filepath))

with openp("system_specifications.json") as fp:
	conf = Bunch(json.load(fp))
with openp("ins_decode.json") as fp:
	opcodes: list[int] = [int(x[2:], base=2) for x in json.load(fp).keys()]
with openp("ins_encode.json") as fp:
	insts: list[int] = json.load(fp)
