#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import logging
import numpy as np
from simulator.instance import Instance
from solver.simpleShop import SimpleShop
from heuristic.simpleHeu import SimpleHeu


np.random.seed(0)


if __name__ == '__main__':
    log_name = "./logs/main.log"
    logging.basicConfig(
        filename=log_name,
        format='%(asctime)s %(levelname)s: %(message)s',
        level=logging.INFO, datefmt="%H:%M:%S",
        filemode='w'
    )

    fp = open("./etc/config.json", 'r')
    sim_setting = json.load(fp)
    fp.close()

    inst = Instance(
        sim_setting
    )
    dict_data = inst.get_data()
    print(dict_data)

    prb = SimpleShop()
    of_exact, sol_exact, comp_time_exact = prb.solve(
        dict_data,
        verbose=True
    )
    print(of_exact, sol_exact, comp_time_exact)
    """
    heu = SimpleHeu(2)
    of_heu, sol_heu, comp_time_heu = heu.solve(
        dict_data
    )
    print(of_heu, sol_heu, comp_time_heu)
    """
    # printing results of a file
    file_output = open(
        "./results/exp_general_table.csv",
        "w"
    )
    """
    file_output.write("method, of, sol, time\n")
    file_output.write("{}, {}, {}, {}\n".format(
        "heu", of_heu, sol_heu, comp_time_heu
    ))
    """
    file_output.write("{}\nPROFIT= {}\n ORDER FOR EACH DAY\n{}\n TIME {}\n".format(
        "exact", of_exact, sol_exact, comp_time_exact
    ))
    file_output.close()
    
