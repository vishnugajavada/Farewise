from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def run(args: list[str]) -> None:
    env=os.environ.copy(); env["PYTHONPATH"]=str(ROOT/"src")+os.pathsep+env.get("PYTHONPATH","")
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True, env=env)

def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("task", choices=["setup","data","train","evaluate","simulate","app","test","lint"])
    task=parser.parse_args().task
    if task=="setup": run(["-m","pip","install","-e",".[dev]"])
    elif task=="data": run(["scripts/prepare_data.py"])
    elif task in {"train","evaluate","simulate"}: run(["-m","farewise.cli",task])
    elif task=="app": run(["-m","streamlit","run","src/farewise/ui/app.py"])
    elif task=="test": run(["-m","pytest","-p","no:cacheprovider","--cov=farewise.data","--cov=farewise.features","--cov=farewise.models","--cov=farewise.evaluation","--cov=farewise.advisor","--cov=farewise.service","--cov-report=term-missing","--cov-fail-under=75"])
    elif task=="lint": run(["-m","ruff","check","src","tests","scripts"])
if __name__=="__main__": main()
