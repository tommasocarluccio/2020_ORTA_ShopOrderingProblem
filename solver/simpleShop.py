import time
import logging
# from pulp import *
import pulp
import numpy as np


class SimpleShop():
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
        suppliers = range(dict_data['num_suppliers'])
        time_period = range(dict_data['time_period'])
        batch=range(1,3)
        initial_inventory=dict_data['initial_inventory']
        pre_order=dict_data['pre_order']

        problem_name = "shop ordering"
        prob = pulp.LpProblem(problem_name, pulp.LpMaximize)  # maximize profit

        # y is binary variable that is 1 if a order to the supplier j at time t is performed
        y = pulp.LpVariable.dicts(
            "y", [(j, t) for j in suppliers for t in time_period],
            cat=pulp.LpBinary
        )
        # y2 is a auxiliary binary variable to linearize minimum function (between inventory and demand of product i at time t)
        y2 = pulp.LpVariable.dicts(
            "y2", [(i, t) for i in items for t in time_period],
            cat=pulp.LpBinary
        )
        # integer variable concerning the extra-cost due to unsatisfied demand
        b = pulp.LpVariable.dicts(
            "b", [(i, t) for i in items for t in time_period], 0,
            cat=pulp.LpInteger
        )
        w = pulp.LpVariable.dicts(
            "w", [(j,l, t) for j in suppliers for l in batch for t in time_period],
            cat=pulp.LpBinary
        )
        # inventory for each product i at time t, depending on inventory of t-1, demand and arrived orders
        #I = pulp.LpVariable.dicts("I", [(i, t) for i in items for t in time_period], lowBound=0, cat=pulp.LpInteger)
        I= pulp.LpVariable.dicts("I", [(i, t) for i in items for t in time_period],lowBound=0, cat=pulp.LpInteger)

        #I2 = pulp.LpVariable.dicts("I", (items, time_period) , lowBound=0, cat=pulp.LpInteger)


        # variable to compute the minimum between inventory and demand, i.e. the amount of product i sold at time t
        sold = pulp.LpVariable.dicts(
            "sold", [(i, t) for i in items for t in time_period], 0,
            cat=pulp.LpInteger
        )
        # order for product i for each time t
        # O= pulp.LpVariable.dicts("O", [(i,j,t) for i in items for j in suppliers for t in time_period],0, cat = pulp.LpInteger)
        O = pulp.LpVariable.dicts("O", [(i, j, t) for i in items for j in suppliers for t in time_period], 0, cat=pulp.LpInteger)

        prob += pulp.lpSum(dict_data['prices'][i] * sold[(i, t)] for i in items for t in time_period)-\
                pulp.lpSum(dict_data['fixed_costs'][j] * y[(j, t)] for j in suppliers for t in time_period) - \
                pulp.lpSum(dict_data['costs'][(i, j)] * O[(i, j, t)] for i in items for j in suppliers for t in time_period) - \
                pulp.lpSum(dict_data['extra_costs'][i] * b[(i, t)] for i in items for t in time_period) - \
                pulp.lpSum(dict_data['holding_costs'][i] * I[(i, t)] for i in items for t in time_period)

        # Set of constraints


        for j in suppliers:
            for t in range(0,dict_data['time_period']):
                prob += pulp.lpSum(O[i, j, t] for i in items) <= dict_data['M'] * y[(j, t)]
        for j in suppliers:
            for t in range(0,dict_data['time_period']):
                prob += pulp.lpSum(O[i, j, t] for i in items) <= dict_data['M'] * y[(j, t)]

        for i in items:
            for t in time_period:
                prob += b[(i, t)] >= (dict_data['demand'][(i, t)] - I[(i, t)])

        for i in items:
            for t in range(1,dict_data['time_period']):
                if t-int(dict_data['time_steps'][i]) < 0:
                    prob += I[(i, t)] == I[(i,t-1)] - dict_data['demand'][(i, t-1)]+pre_order[(i,t-int(dict_data['time_steps'][i]) )]
                else:
                    prob += I[(i, t)] == I[(i, t - 1)] - dict_data['demand'][(i, t-1)] + pulp.lpSum(O[(i, j, t-int(dict_data['time_steps'][i]))] for j in suppliers)

        for i in items:
            prob.addConstraint(pulp.LpConstraint(
            e=-I[(i, 0)],
            sense=pulp.LpConstraintEQ,
            rhs=-initial_inventory[i]))

        for i in items:
            for t in time_period:
                #prob += dict_data['demand'][(i, t)] - I[(i, t)] <= dict_data['M'] * y2[(i, t)]
                #prob += I[(i, t)] - dict_data['demand'][(i, t)] <= dict_data['M'] * (1 - y2[(i, t)])

                prob += sold[(i, t)] <= I[(i, t)]
                prob += sold[(i, t)] <= dict_data['demand'][(i, t)]
                #prob += sold[(i, t)] >= I[(i, t)] - dict_data['M'] * (1 - y2[(i, t)])
                #prob += sold[(i, t)] >= dict_data['demand'][(i, t)] - dict_data['M'] * (y2[(i, t)])

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

        #for v in sol:
           #print(v.name, "=", v.varValue)

        print(pulp.LpStatus[prob.status])
        sol_o = np.zeros((dict_data['num_products'], dict_data['time_period']))
        for t in range(0,dict_data['time_period']):
            for i in items:
                result = 0
                for j in suppliers:
                    result += pulp.value(O[(i, j, t)])
                sol_o[(i, t)] = result

        print(sol_o)

        for var in sol:
            logging.info("{} {}".format(var.name, var.varValue))

            if "O_" in var.name:
                pass
                # sol_o[int(var.name.replace("O_", ""))] = abs(var.varValue)

        logging.info("\n\tof: {}\n\tsol:\n{} \n\ttime:{}".format(
            of, sol_o, comp_time)
        )
        logging.info("#########")

        return of, sol_o, comp_time
