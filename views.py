import json

import texttable
from Executor.simulator import Executor, Mode

def process(bin_cod: str, token: str) -> str:
	Executor.load_code(bin_cod[1])
	srcmap = {x[0]: x[1] for x in zip(bin_cod[0], bin_cod[1].split("\n"))}
	# bin_out = bin_cod[1]
	mode = Mode.STEP
	
	output = Executor.process(pipelined=True, token=token, action=mode)
	out = output["state_dump"]
	pl = output["pipeline"]
	mem = output["mem_dump"]
	token = output["token"]
	regs = "\n".join([f"{x}|{int(x, base=2)}" for x in output["regs"].split()])
	state = json.dumps([x.__dict__ for x in output["state"]])
	
	pipeline = [[" " for x in range(len(pl))] for y in range(len(bin_cod[0]))]
	phases = ["F", "D", "X", "M", "W"]
	
	tbl = texttable.Texttable(max_width=500)
	for cycle_num, cycle in enumerate(pl):
		for i in range(5):
			if cycle[i] != -1:
				pipeline[cycle[i]][cycle_num] = phases[i]
	tbl.add_rows(pipeline, header=False)
	pipeline = tbl.draw()
	
	content=json.dumps(
		{
			# "bin": Bbin,
			"src_map": json.dumps(srcmap),
			"out": out,
			"pipeline": str(pipeline),  # json dumps escapes characters which i dont want
			"memory": mem,
			"state": state,
			"regs": regs,
			"token": token
		}
	)
	
	return content
