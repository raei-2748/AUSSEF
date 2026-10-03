#!/bin/zsh
# Run any Experiment 16 script in a throwaway uv environment (geo + stats packages).
# Usage: ./run.sh script.py [args]
exec uv run --no-project --python 3.13 --with geopandas==1.1.4 --with pyogrio==0.13.0 --with shapely==2.1.2 \
  --with openpyxl --with statsmodels --with scipy --with pyarrow --with matplotlib python "$@"
