# tgc
Tetris Game Charger

# Steps

https://packaging.python.org/en/latest/flow/

1. cd ~/tgc
2. 'python3 -m build --sdist src' -> Successfully built tgc-0.0.0.tar.gz
3. 'python3 -m build --wheel src'
4. python3 -m twine upload --repository testpypi dist/*

https://test.pypi.org/project/tgc/

<!-- 4. twine upload dist/tgc-0.0.0.tar.gz dist/tgc-0.0.0-py3-none-any.whl -->

