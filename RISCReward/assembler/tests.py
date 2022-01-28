import os

from django.test import TestCase
from .modules.Assembler.assembler import parse
from .modules.Executor.simulator import Executor

# Create your tests here.

class AsmTest(TestCase):
	def setUp(self) -> None:
		here = os.path.dirname(os.path.realpath(__file__))
		self.asm_dir = here+"/modules/testcases/assembly/hardBin"
		self.bin_dir = here+"/modules/testcases/bin/hard"
		self.fin_dir = here+"/modules/testcases/traces/hard"
		self.asms = list(os.walk(self.asm_dir))[0][2]
		self.bins = list(os.walk(self.bin_dir))[0][2]
		self.fins = list(os.walk(self.fin_dir))[0][2]
		self.maxDiff = None
		
	def testAssembler(self):
		for a, b, f in zip(self.asms, self.bins, self.fins):
			with self.subTest(msg=a):
				with open(self.asm_dir+"/"+a) as fl:
					asm = fl.read()
				asm_out = parse(asm)
				
				with open(self.bin_dir+"/"+b) as fl:
					byt = fl.read()
					self.assertEqual(asm_out.strip(), byt.strip())
				
	def testExecutor(self):
		E = Executor()
		for b, f in zip(self.bins, self.fins):
			with self.subTest(msg=b):
				with open(self.bin_dir+"/"+b) as fl:
					byt = fl.read()
				
				E.load_code(byt)
				byt_out = E.process(pipelined=False)
				with open(self.fin_dir+"/"+f) as fl:
					fin = fl.read()
					x = byt_out.strip()
					self.assertEqual(x, fin.strip())
	
	def testPipelined(self):
		E = Executor()
		for b, f in zip(self.bins, self.fins):
			with self.subTest(msg=b):
				if '09' in b:
					return
				with open(self.bin_dir+"/"+b) as fl:
					byt = fl.read()
				
				E.load_code(byt)
				byt_out = E.process(pipelined=True)
				with open(self.fin_dir+"/"+f) as fl:
					fin = fl.read()
					self.assertEqual(byt_out.strip(), fin.strip())
	