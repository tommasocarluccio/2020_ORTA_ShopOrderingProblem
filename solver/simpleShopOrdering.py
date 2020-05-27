# -*- coding: utf-8 -*-
import time
import logging
# from pulp import *
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
        items = range(dict_data['num_products'])
        suppliers=range(dict_data['num_suppliers'])
        time_period=range(dict_data['time_period'])
        #print(dict_data['costs'][14])


        O = pulp.LpVariable.dicts(
            "O", [(i, j, t) for i in items for j in suppliers for t in time_period],
            lowBound=0,
            cat=pulp.LpInteger
        )
        y = pulp.LpVariable.dicts(
            "y", [(j, t) for j in suppliers for t in time_period],
            cat=pulp.LpBinary
        )
        b = pulp.LpVariable.dicts(
            "b", [(i, t) for i in items for t in time_period],
            cat=pulp.LpInteger
        )

        # LpContinuous

        problem_name = "shop ordering"

        prob = pulp.LpProblem(problem_name, pulp.LpMinimize)
        prob += pulp.lpSum([dict_data['fixed_costs'][j] * y[(j, t)] for j in suppliers for t in time_period]) +\
                pulp.lpSum([dict_data['costs'][(i, j)]*O[(i, j, t)] for i in items for j in suppliers for t in time_period]) + \
                pulp.lpSum([(dict_data['inventory'][(i, t-1)]-dict_data['demand'][(i, t)]+sum([O[(i, j, t-dict_data['time_steps'][i] if t-dict_data['time_steps'][i] > 0 else 0)] for j in suppliers])) * dict_data['holding_costs'][i] for i in items for t in time_period]) + \
                pulp.lpSum([dict_data['extra_costs'][i] * b[(i, t)] for i in items for t in time_period]), "obj_func"
        #prob += pulp.lpSum([dict_data['sizes'][i] * x[i] for i in items]) <= dict_data['max_size'], "max_vol"
        #prob+= pulp.lpSum([O[(i, j, t)] for i in items for j in suppliers for t in time_period]) >=0
        #pulp.lpSum([dict_data['inventory'][(i, t)] * dict_data['holding_costs'][i] for i in items for t in time_period]) +\

        for i in items:
            for j in suppliers:
                for t in time_period:
                    prob += O[(i, j, t)] >=0

        for j in suppliers:
            for t in time_period:
                prob += pulp.lpSum([O[(i, j, t)]for i in items]) <= dict_data['M']*y[(j, t)]
                prob += b[(i, t)] == (max(dict_data['demand'][(i, t)]-dict_data['inventory'][(i, t)],0))
        """
        for t in time_period:
            for i in items:
                dict_data['inventory'][(i, t)]= dict_data['inventory'][(i, t-1)] +\
                                                O[(i, j, t-dict_data['time_steps'][i] if t-dict_data['time_steps'][i] > 0 else 0 )]-\
                                                dict_data['demand'][i]
        """
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

        sol_x = [0] * dict_data['num_products']
        for var in sol:
            logging.info("{} {}".format(var.name, var.varValue))
            if "X_" in var.name:
                sol_x[int(var.name.replace("X_", ""))] = abs(var.varValue)
        logging.info("\n\tof: {}\n\tsol:\n{} \n\ttime:{}".format(
            of, sol_x, comp_time)
        )
        logging.info("#########")
        return of, sol_x, comp_time
