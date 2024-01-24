
#! /usr/bin/bash

cd ${HOME}/tgc
mamba activate base
rm -rf src/dist
python3 -m build --sdist src
python3 -m build --wheel src
python3 -m twine upload --repository testpypi src/dist/*