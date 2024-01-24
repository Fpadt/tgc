 <img src="https://github.com/Fpadt/tgc/blob/main/src/tgc_jads_2324/Enexis_JADS.png" alt="JADS_2324-C2.Enexis" style="width:12%; float:right">
 
# TGC - Tetris Game Charger <a href="https://test.pypi.org/project/tgc-jads-2324/" target="_blank" rel="noopener noreferrer"><img src="https://github.com/Fpadt/tgc/blob/main/src/tgc_jads_2324/TGC_tran.png" align="right" height="300" /></a>



The Tetris Game Charger (TGC) is the result of the group project of **C2.Enexis of class 23/24** of [Jheronymous Academy of Data Science (JADS).](https://www.jads.nl/education/data-science-and-ai-for-professionals/)

This [package](https://test.pypi.org/project/tgc-jads-2324/) is a toy package which leverages simulation using [Salabim](https://www.salabim.org/) to test multiple algorithms for scheduling electric vehicles (EV) in a charging facility.

Next to the normal priority rules, e.g FIFO, SPT, EDD we also implemented OLP (OnLine Linear Programming) and RL (Reinforcement Learning). The latter is however not available via this package.

## JADS 23/34 - C2.Enexis

 TGC members           | Role                             | Quote
:----------------------|:---------------------------------|:------------------
 Alex Teeuwen          | Reinforcement learning engineer  | `I taught my computer to learn from its mistakes`
 Anne-Marie Van Nes    | Organizer and criticaster        | `my rubber ducks are in a row, but keep floating away`
 Dominique Fürst       | Statistical distributions Expert | `In the world of data, I fit in like an outlier at a mean party.`
 Floris Padt           | OLP - engineer                   | `I love linear solutions. If only life wasn't so nonlinear.`
 Henk Koster           | Presentor & business owner       | `Presenting a use case: where optimism meets data science reality.` 

## OLP
The idea of OLP originates from this paper: 
[Guo et al. - 2017 - Optimal online adaptive electric vehicle charging](http://netlab.caltech.edu/assets/publications/Guo-2017-OLP.pdf).

### Solver
This packages use by default the glptk solver. Other solvers like mosek, ipopt (MH27), cplex or gurobi can be configured but do require a trial license setup.

## Package Installation

[package on test.pypi](https://test.pypi.org/project/tgc-jads-2324/)

1. create new environment *(recommended but optional)*
2. ```pip install -i https://test.pypi.org/simple/ tgc-jads-2324```

## References
The following links show the prework done to come to this model. 
The jupyter notebooks contain explanation and pyton coding with results. 

The last link is a downloadable excel file containing a lite OLP model which can be solved by the Excel Solver Add-in (needs to be activated)

- [Queuing Theory (Waiting Line Models)](https://github.com/Fpadt/salabim_jads/blob/main/3rd-report/jads_3rd_interim_report.ipynb)
- [OLP: Online Linear Programming](https://github.com/Fpadt/salabim_jads/blob/main/floris_tetris/olp/tgc_olp.ipynb)
- [OLP lite in Excel](https://github.com/Fpadt/salabim_jads/blob/main/floris_tetris/olp/TGC_LP.xlsx)
