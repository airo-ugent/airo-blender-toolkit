# airo-blender-toolkit
Python package to faciliate the usage of the Blender python API @ AIRO UGent

Currently only tested on Blender 3.0.

## Quick Installation
```bash
cd ~/blender-3.0.0-linux-x64/3.0/python/bin
./python3.9 -m ensurepip
./python3.9 -m pip install -e ~/airo-blender-toolkit
```

## Installation with venvify

Turn Blender python into a venv-like environment:
```bash
cd ~/blender-3.0.0-linux-x64/3.0/python/bin
./python3.9 -m ensurepip
./pip3 install venvify
./venvify .. --env_name blender
source activate
```
Simply install the package as in a venv:
```
pip3 install -e ~/airo-blender-toolkit
```
