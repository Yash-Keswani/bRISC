import json

from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, QueryDict
from django.views.decorators.http import require_POST
from .modules.Assembler.assembler import parse
from .modules.Executor.simulator import Executor
import texttable

def index(request: HttpRequest):
	return render(request, "assembler/index.html", {})

@require_POST
def process(request: HttpRequest) -> HttpResponse:
	bin_cod = parse(request.POST.get(key="my_code"))
	if (bin_cod[0][0] != -1):
		Executor.load_code(bin_cod[1])
		Bbin = "".join([f"{x[0]}) {x[1]}\n" for x in zip(bin_cod[0], bin_cod[1].split("\n"))])
		out, pl = Executor.process(pipelined=True)
		pipeline = [[" " for x in range(len(pl))] for y in range(len(bin_cod[0]))]
		phases = ["F", "M", "W", "D", "X"]
		
		tbl = texttable.Texttable()
		for cycle_num, cycle in enumerate(pl):
			for i in range(5):
				if cycle[i] != -1:
					pipeline[cycle[i]][cycle_num] = phases[i]
		tbl.add_rows(pipeline, header=False)
		pipeline = tbl.draw()
		
	else:
		Bbin = bin_cod[1]
		out = ""
		pipeline = ""
	return HttpResponse(
		content=json.dumps(
			{
				"bin": Bbin,
				"out": out,
				"pipeline": str(pipeline)
			}
		)
	)
