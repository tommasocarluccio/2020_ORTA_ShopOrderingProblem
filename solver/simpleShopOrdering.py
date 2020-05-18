# -*- coding: utf-8 -*-
import time
import logging
#from pulp import *
import pulp

class SimpleKnapsack():
    def __init__(self):
        pass

    def solve(
        self, dict_data, time_limit=None,
        gap=None, verbose=False
    ):
        """[summary]
        
        Arguments:
            dict_data {[type]} -- [description]
        
        Keyword Arguments:
            time_limit {[type]} -- [description] (default: {None})
            gap {[type]} -- [description] (default: {None})
            verbose {bool} -- [description] (default: {False})
        
        Returns:
            [type] -- [description]
        """
        logging.info("#########")
        items = range(dict_data['n_items'])

        x = pulp.LpVariable.dicts(
            "X", items,
            lowBound=0,
            cat=pulp.LpInteger
        )
        # LpContinuous

        problem_name = "shop ordering"

        prob = pulp.LpProblem(problem_name, pulp.LpMaximize)
        prob += pulp.lpSum([dict_data['profits'][i] * x[i] for i in items]) , "obj_func"
        prob += pulp.lpSum([dict_data['sizes'][i] * x[i] for i in items]) <= dict_data['max_size'], "max_vol"

        prob.writeLP("./logs/{}.lp".format(problem_name))

        msg_val = 1 if verbose else 0
        start = time.time()
        solver = pulp.solvers.COIN_CMD(
            msg=msg_val,
            maxSeconds=time_limit,
            fracGap=gap
        )
        solver.solve(prob)
        end = time.time()
        logging.info("\t Status: {}".format(pulp.LpStatus[prob.status]))

        sol = prob.variables()
        of = pulp.value(prob.objective)
        comp_time = end - start

        sol_x = [0] * dict_data['n_items']
        for var in sol:
            logging.info("{} {}".format(var.name, var.varValue))
            if "X_" in var.name:
                sol_x[int(var.name.replace("X_", ""))] = abs(var.varValue)
        logging.info("\n\tof: {}\n\tsol:\n{} \n\ttime:{}".format(
            of, sol_x, comp_time)
        )
        logging.info("#########")
        return of, sol_x, comp_time
