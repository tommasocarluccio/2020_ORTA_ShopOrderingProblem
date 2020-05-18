# Project Template

In this file, we give you some general guideline and advices for the project. You need two components:

1. Python 3.6
1. CBC solver

## Python

Linux users should have python already installed in their PC. For the other users I strongly recomment to install **Anaconda** and to use its terminal for installing new packages. You can find details [here](https://www.anaconda.com/distribution/) and [there](https://www.anaconda.com/distribution/#download-section). 


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
and enjoy...


## Report

For the final report you can use both Word or Latex.
I strongly suggest the second one because it is more suited to deal with equations, models, graphs, etc.
A really nice website that enables you to work together and deals with all the package issues of latex is [Overleaf](https://www.overleaf.com/). In the folder *report* you have a latex template that you can directly load on overleaf.
A useful link for creating latex table is [here](https://www.tablesgenerator.com/latex_tables)
The folder report contains a latex template with some examples.


## Text Editor

In order write good code you need a good editor. The best one that I recomend are:

1. [Visual Studio Code](https://code.visualstudio.com/) free;
1. [Sublime Text](https://www.sublimetext.com/) free for non commercial usage;
1. [PyCharm](https://www.jetbrains.com/pycharm/) free for students.

