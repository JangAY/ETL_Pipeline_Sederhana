import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent   # .. (folder project)
sys.path.append(str(ROOT_DIR))