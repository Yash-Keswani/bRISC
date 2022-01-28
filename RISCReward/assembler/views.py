import json

from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from django.views.decorators.http import require_POST
from .modules.Assembler.assembler import parse
from .modules.Executor.simulator import Executor

def index(request: HttpRequest):
	return render(request, "assembler/index.html", {})

@require_POST
def process(request: HttpRequest) -> HttpResponse:
	bin_cod = parse(request.POST.get(key="my_code"))
	if (bin_cod[0][0] != -1 and False):
		Executor.load_code(bin_cod[1])
		Bbin = "".join([f"{x[0]}) {x[1]}\n" for x in zip(bin_cod[0], bin_cod[1].split("\n"))])
		out = Executor.process(pipelined=False)
	else:
		Bbin = bin_cod[1]
		out = ""
	return HttpResponse(
		content=json.dumps(
			{
				"bin": Bbin,
				"out": out
			}
		)
	)
