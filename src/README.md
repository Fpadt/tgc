 
# TGC - Tetris Game Charger 

The Tetris Game Charger (TGC) is the result of the group project of **C2.Enexis of class 23/24** of [Jheronymous Academy of Data Science (JADS).](https://www.jads.nl/education/data-science-and-ai-for-professionals/)

This [package](https://test.pypi.org/project/tgc-jads-2324/) is a toy package which leverages simulation using [Salabim](https://www.salabim.org/) to test multiple algorithms for scheduling electric vehicles (EV) in a charging facility.

Next to the normal priority rules, e.g FIFO, SPT, EDD we also implemented OLP (OnLine Linear Programming) and RL (Reinforcement Learning). The latter is however not available via this package.

## JADS 23/34 - C2.Enexis

- Alex Teeuwen
- Anne-Marie Van Nes
- Dominique Fürst
- Floris Padt
- Henk Koster

## OLP
The idea of OLP originates from this paper: 
[Guo et al. - 2017 - Optimal online adaptive electric vehicle charging](http://netlab.caltech.edu/assets/publications/Guo-2017-OLP.pdf).

### Solver
This packages use by default the glptk solver. Other solvers like mosek, ipopt (MH27), cplex or gurobi can be configured but do require a trial license setup.

## Package Installation

[package on test.pypi](https://test.pypi.org/project/tgc-jads-2324/)

1. create new environment *(recommended but optional)*
2. ```pip install -i https://test.pypi.org/simple/ tgc-jads-2324```
