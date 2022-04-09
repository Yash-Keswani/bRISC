import os
from pathlib import Path

CACHE_DIR = "RISCReward/assembler/cache/"
def prune():
	paths = sorted(Path(CACHE_DIR).iterdir(), key=os.path.getmtime)
	for x in paths[0:-100]:
		os.remove(x)

'''
if __name__ == "__main__":
	prune()
'''
