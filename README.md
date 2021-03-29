# Shop ordering problem

The purpose of this project is the creation of a mathematical model to describe the multi- period ordering planning of a generic store. The LP formulation is implemented in a Python environment, exploiting the PuLP library. The analysis on the case study is performed consid- ering both an exact and a heuristic solution. After some instances generation, computational results are provided to offer a complete overview of the project and its functionalities.

## Running the code

To run the code you need two components:

1. Python 3.6
2. CBC solver

## CBC solver
In order to install CBC, for Linux users just run the following command:
```
apt-get install coinor-cbc
```
For other users, I suggest to follow the instructions on the [CBC web page](https://projects.coin-or.org/Cbc).

For Windows users, you need to add the path of the executable files of both solvers (e.g. *CoinAll-1.60-win64-intel11.1/bin*) to the PATH variable using this [tutorial](https://www.computerhope.com/issues/ch000549.htm). Then Restart Windows. 
In order to check if the procedure works, you can run
~~~
cbc.exe
~~~
from your terminal.

If you are not able to install CBC you can also use GLPK, you can find the instruction [here](https://www.gnu.org/software/glpk/).

## Python packages:
Probably you will need to install several packages (e.g., pulp, numpy, etc). In linux my suggestion is to use pip
~~~
pip3 install <package name>
~~~
e.g., 
~~~
pip3 install pulp
~~~
For windows is suggest to use conda.
~~~
conda install -c conda-forge pulp 
~~~


## Run the code:
Run the code by writing in the terminal
```
python3 main.py
```
