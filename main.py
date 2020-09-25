#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import logging
import numpy as np
from simulator.instance import Instance
from solver.simpleShop import SimpleShop
from heuristic.simpleHeuGreedy import simpleHeuGreedy
from heuristic.simpleHeuGreedy_not_optimized import simpleHeuGreedy_not_optimized
import matplotlib.pyplot as plt


np.random.seed(0)

if __name__ == '__main__':
    log_name = "./main.log"
    logging.basicConfig(
        filename=log_name,
        format='%(asctime)s %(levelname)s: %(message)s',
        level=logging.INFO, datefmt="%H:%M:%S",
        filemode='w'
    )

    # Open settings file
    fp = open("./etc/config_proportionate.json", 'r')
    sim_setting = json.load(fp)
    fp.close()

    # Create instance of the problem to be solved
    inst = Instance(sim_setting)
    dict_data = inst.get_data()

    # Solve using the exact method
    prb = SimpleShop()
    of_exact, sol_exact, comp_time_exact, sol_y, sol_discount, sol_O_with_j = prb.solve(dict_data,verbose=True)
    print(of_exact, sol_exact, comp_time_exact)

    # Solve using a greedy heuristic method
    epsilon=0.03
    heu = simpleHeuGreedy()
    of_heu, sol_heu, comp_time_heu = heu.solveGreedy(dict_data,epsilon,verbose=True)
    print(of_heu, sol_heu, comp_time_heu)

    # print results as a file
    file_output = open("./results/exp_general_table.csv","w")
    file_output.write("method, of, sol, time\n")
    file_output.write("{}, {}, {}, {}\n".format("heu", of_heu, sol_heu, comp_time_heu))
    file_output.write("{}\nPROFIT= {}\n ORDER FOR EACH DAY\n{}\n TIME {}\n".format("exact", of_exact, sol_exact, comp_time_exact))
    file_output.close()

    # print results on terminal
    print("Exact solution:")
    print(of_exact, sol_exact, comp_time_exact," \n")
    print("Greedy Heuristic solution:")
    print(of_heu, sol_heu, comp_time_heu, "\n")


    # Evaluate an over/under estimation of the demand
    #moreDemand = np.array(range(-500,500))
    #of_overDemand = prb.compareDemand(of_exact, dict_data, sol_y, sol_discount, sol_exact, sol_O_with_j, moreDemand, verbose=True)

    """
    # Create graphs with different value of time period in the config 
    # Compare exact and heuristic methods

    of_ex_tot=[]
    of_heu_tot=[]
    of_heu_not_tot=[]
    time_ex_tot=[]
    time_heu_tot=[]
    time_heu_not_tot=[]
    T_executions=range(1,8,1) # Time steps used for different executions of the program
    for i in T_executions:
        # Open configuration file
        fp = open("./etc/config_proportionate.json", 'r')
        sim_setting = json.load(fp)
        fp.close()

        # Change time period of the simulation in the json
        sim_setting["time_period"]= i

        # Create instance of simultion
        inst = Instance(sim_setting)
        dict_data = inst.get_data()

        # Run exact solution
        prb = SimpleShop()
        of_exact, sol_exact, comp_time_exact, sol_y, sol_discount, sol_O_with_j = prb.solve(dict_data,verbose=True)
        print(of_exact, sol_exact, comp_time_exact)
        of_ex_tot.append(of_exact)
        time_ex_tot.append(comp_time_exact)

        # Run heuristic solution
        heu = simpleHeuGreedy()
        of_heu, sol_heu, comp_time_heu = heu.solveGreedy(dict_data,0,verbose=True)
        of_heu_tot.append(of_heu)
        time_heu_tot.append(comp_time_heu)

        # Run heuristic solution not optimized
        heu_not_optimized = simpleHeuGreedy_not_optimized()
        of_heu_not, sol_heu_not, comp_time_heu_not = heu_not_optimized.solveGreedy(dict_data,100,verbose=True)
        of_heu_not_tot.append(of_heu_not)
        time_heu_not_tot.append(comp_time_heu_not)

    print(of_ex_tot)
    print(of_heu_tot)
    print(time_ex_tot)
    print(time_heu_tot)
    # Profit
    plt.plot(T_executions, of_ex_tot, 'r', T_executions, of_heu_tot, 'b', T_executions, of_heu_not_tot, 'g')
    plt.xlabel('Time steps')
    plt.ylabel('Profit')
    plt.title('Profit with different time periods')
    labels=["exact", "heuristic optimized", "heuristic not optimized"]
    plt.legend(labels)
    plt.grid(True)
    plt.show()
    # Execution time
    #plt.plot(T_executions, time_ex_tot, 'r', T_executions, time_heu_tot, 'b', T_executions, time_heu_not_tot, 'g')
    plt.plot(T_executions, time_ex_tot, 'r', T_executions, time_heu_not_tot,'b')
    plt.xlabel('Time steps')
    plt.ylabel('Execution time')
    plt.title('Execution time with different time periods')
    labels=["exact", "heuristic"]
    plt.legend(labels)
    plt.grid(True)
    plt.show()
    
    # Profit difference between of exact and heuristic depending on optimization
    diff=[]
    diff_not=[]
    for i in range(0,7):
        dif=of_ex_tot[i]-of_heu_tot[i]
        dif_not=of_ex_tot[i]-of_heu_not_tot[i]
        diff.append(dif)
        diff_not.append(dif_not)

    plt.plot(T_executions, diff, 'r', T_executions, diff_not, 'b')
    plt.xlabel('Time period')
    plt.ylabel('Profit difference between of exact and heuristic')
    plt.title('Profit difference between of exact and heuristic depending on optimization')
    labels=["optimized", "not optimized"]
    plt.legend(labels)
    plt.grid(True)
    plt.show()
    """

    """
    # Evaluate heuristic with different thresholds

    thresholds=range(0,100,10)
    profits=[]
    for thr in thresholds:
        # Open configuration file
        fp = open("./etc/config_proportionate.json", 'r')
        sim_setting = json.load(fp)
        fp.close()

        # Create instance of simultion
        inst = Instance(sim_setting)
        dict_data = inst.get_data()

        threshold=thr
        # Run heuristic solution
        heu = simpleHeuGreedy_not_optimized()
        of_heu, sol_heu, comp_time_heu = heu.solveGreedy(dict_data, threshold, verbose=True)
        profits.append(of_heu)
        # SAVE PROFIT

    # Profit
    plt.plot(thresholds, profits, 'r')
    plt.xlabel('thresholds')
    plt.ylabel('Heuristic Profit')
    plt.title('Profit as threshold goes up')
    plt.grid(True)
    plt.show()
    """

    """
    # Create graphs with different value of time period in the config 
    # Compare exact and heuristic methods

    of_heu_tot=[]
    epsilons=np.arange(0,1,0.05) # Time steps used for different executions of the program
    for e in epsilons:
        # Open configuration file
        fp = open("./etc/config_proportionate.json", 'r')
        sim_setting = json.load(fp)
        fp.close()

        # Create instance of simultion
        inst = Instance(sim_setting)
        dict_data = inst.get_data()

        epsilon=e
        # Run heuristic solution
        heu = simpleHeuGreedy()
        of_heu, sol_heu, comp_time_heu = heu.solveGreedy(dict_data,epsilon,verbose=True)
        of_heu_tot.append(of_heu)

    print(of_heu_tot)
    print(epsilons)
    # Profit
    plt.plot(epsilons, of_heu_tot, 'r')
    plt.xlabel('epsilon')
    plt.ylabel('Profit')
    plt.title('Profit with different soft policies epsilon value')
    plt.grid(True)
    plt.show()

    # Open configuration file
    fp = open("./etc/config_proportionate.json", 'r')
    sim_setting = json.load(fp)
    fp.close()

    # Create instance of simultion
    inst = Instance(sim_setting)
    dict_data = inst.get_data()

    epsilon=0.05
    # Run heuristic solution
    heu = simpleHeuGreedy()
    of_heu, sol_heu, comp_time_heu = heu.solveGreedy(dict_data,epsilon,verbose=True)
    print(of_heu)
    """

