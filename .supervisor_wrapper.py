#!/usr/bin/env python3
import sys
import subprocess

args = []
args.append('oc-collab')
args.append('agent')
args.append('--interval')
args.append('30')

sys.exit(subprocess.run(args).returncode)
