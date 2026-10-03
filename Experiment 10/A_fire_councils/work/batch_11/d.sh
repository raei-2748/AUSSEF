#!/bin/bash
# usage: d.sh id council fy type url landing
python3 "/Users/ray/Research/AUSSEF - Local/Experiment 10/A_fire_councils/tools/dl.py" --batch 11 --region_id "$1" --council "$2" --fy "$3" --doc_type "$4" --url "$5" --landing "${6:-}" 2>&1 | tail -2
