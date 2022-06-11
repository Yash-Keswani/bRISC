import json

import texttable
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .modules.Assembler.assembler import parse
from .modules.Executor.simulator import Executor, Mode

def index(request: HttpRequest):
	return render(request, "assembler/index.html", {})

def index2(request: HttpRequest):
	return render(request, "assembler/index2.html", {})

def specs(request: HttpRequest):
	return render(request, "assembler/isa_specs.json", {}, content_type='application/json')

@require_POST
def process(request: HttpRequest) -> HttpResponse:
	data = json.loads(request.body)
	bin_cod = parse(data["my_code"])
	if (bin_cod[0][0] != -1):
		Executor.load_code(bin_cod[1])
		# Bbin = "".join([f"{x[0]}) {x[1]}\n" for x in zip(bin_cod[0], bin_cod[1].split("\n"))])
		# srcmap = bin_cod[0]
		srcmap = {x[0]: x[1] for x in zip(bin_cod[0], bin_cod[1].split("\n"))}
		# bin_out = bin_cod[1]
		if data.get("mode") == 'run':
			mode = Mode.RUN
		elif data.get("mode") == 'debug':
			mode = Mode.DEBUG
		elif data.get("mode") == 'step':
			mode = Mode.STEP
		else:
			raise AssertionError("Mode must be run, debug, or step")
		
		output = Executor.process(pipelined=False, token=data.get("session_token"), action=mode)
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
	
	else:
		out = bin_cod[1]
		token = None
		bin_out = srcmap = pipeline = mem = state = regs = ""
	
	return HttpResponse(
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
	)
