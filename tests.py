import os

from unittest import TestCase
from Executor.simulator import Executor

# Create your tests here.

class AsmTest(TestCase):
	def setUp(self) -> None:
		here = os.path.dirname(os.path.realpath(__file__))
		self.bin_dir = here + "/testcases/bin/hard"
		self.fin_dir = here + "/testcases/traces/hard"
		self.bins = list(os.walk(self.bin_dir))[0][2]
		self.fins = list(os.walk(self.fin_dir))[0][2]
		self.maxDiff = None
	
	def testExecutor(self):
		E = Executor()
		for b, f in zip(self.bins, self.fins):
			# if '2' in b:
			#	break
			with self.subTest(msg=b):
				with open(self.bin_dir + "/" + b) as fl:
					byt = fl.read()
				
				E.load_code(byt)
				byt_out = E.process(pipelined=False)
				byt_out = byt_out["reg_dump"] + byt_out["mem_dump"]
				with open(self.fin_dir + "/" + f) as fl:
					fin = fl.read()
					x = byt_out.strip()
					self.assertEqual(x, fin.strip())
	
	def testPipelined(self):
		E = Executor()
		for b, f in zip(self.bins, self.fins):
			with self.subTest(msg=b):
				with open(self.bin_dir + "/" + b) as fl:
					byt = fl.read()
				
				E.load_code(byt)
				byt_out = E.process(pipelined=True)
				byt_out = byt_out["reg_dump"] + byt_out["mem_dump"]
				with open(self.fin_dir + "/" + f, "r") as fl:
					fin = fl.read()
				self.assertEqual(byt_out.strip(), fin.strip())
