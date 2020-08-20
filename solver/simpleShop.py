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
        batch = [0, 1, 2, 3]
        initial_inventory = dict_data['initial_inventory']
        pre_order = dict_data['pre_order']

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
        w = pulp.LpVariable.dicts("w", [(j, l, t) for j in suppliers for l in batch for t in time_period],0,
                                  cat=pulp.LpBinary)

        # Needed for constraint: https://math.stackexchange.com/questions/3029175/question-to-the-solution-of-indicator-variable-if-x-is-in-specific-range?noredirect=1&lq=1
        delta = pulp.LpVariable.dicts("delta", [(j, l, t) for j in suppliers for l in batch for t in time_period],0,
                                      cat=pulp.LpBinary)

        # inventory for each product i at time t, depending on inventory of t-1, demand and arrived orders
        #I = pulp.LpVariable.dicts("I", [(i, t) for i in items for t in time_period], lowBound=0, cat=pulp.LpInteger)
        I= pulp.LpVariable.dicts("I", [(i, t) for i in items for t in time_period], 0, cat=pulp.LpInteger)

        #I2 = pulp.LpVariable.dicts("I", (items, time_period) , lowBound=0, cat=pulp.LpInteger)


        # variable to compute the minimum between inventory and demand, i.e. the amount of product i sold at time t
        """
        sold = pulp.LpVariable.dicts(
            "sold", [(i, t) for i in items for t in time_period], 0,
            cat=pulp.LpInteger
        )
        # use this if long constraint (so 0 as lower bound)
        """
        sold = pulp.LpVariable.dicts(
            "sold", [(i, t) for i in items for t in time_period],
            cat=pulp.LpInteger
        )
        y3= pulp.LpVariable.dicts(
            "y3", [(i, t) for i in items for t in time_period],0,
            cat=pulp.LpBinary
        )
        dem = pulp.LpVariable.dicts(
            "dem", [(i, t) for i in items for t in time_period],
            cat=pulp.LpInteger
        )
        discount = pulp.LpVariable.dicts("discount", [(j, t) for j in suppliers for t in time_period], lowBound=0,
                                         cat=pulp.LpContinuous)
        # order for product i for each time t
        O = pulp.LpVariable.dicts("O", [(i, j, t) for i in items for j in suppliers for t in time_period], 0, cat=pulp.LpInteger)

        prob += pulp.lpSum(dict_data['prices'][i] * sold[(i, t)] for i in items for t in range(0,dict_data['time_period'])) -\
                pulp.lpSum(dict_data['fixed_costs'][j] * y[(j, t)] for j in suppliers for t in time_period) - \
                pulp.lpSum(dict_data['costs'][(i, j)] * O[(i, j, t)] for i in items for j in suppliers for t in time_period) - \
                pulp.lpSum(dict_data['extra_costs'][i] * b[(i, t)] for i in items for t in range(0, dict_data['time_period'])) - \
                pulp.lpSum(dict_data['holding_costs'][i] * I[(i, t)] for i in items for t in range(0, dict_data['time_period'])) + \
                pulp.lpSum(discount[(j, t)] for j in suppliers for t in time_period)

        # Set of constraints

        for j in suppliers:
            for t in range(0, dict_data['time_period']):
                prob += pulp.lpSum(O[i, j, t] for i in items) <= dict_data['M'] * y[(j, t)]

        for i in items:
            for t in time_period:
                prob += b[(i, t)] >= (dict_data['demand'][(i, t)] - I[(i, t)])
                # prob += I[(i, t)] == 0

        for i in items:
            for t in range(1,dict_data['time_period']):
                if t-int(dict_data['time_steps'][i]) < 0:

                    prob += dem[(i, t)] == (I[(i, t - 1)] - sold[(i, t - 1)] + pre_order[(i, t - int(dict_data['time_steps'][i]))])

                    prob += I[(i, t)] <= dict_data['M'] * y3[(i, t)]
                    prob += I[(i, t)] <= dem[(i, t)]+dict_data['M']*(1-y3[(i, t)])

                else:
                    prob += dem[(i, t)] == I[(i, t - 1)] - sold[(i, t-1)] + pulp.lpSum(O[(i, j, t-int(dict_data['time_steps'][i]))] for j in suppliers)
                    prob += I[(i, t)] <= dict_data['M'] * y3[(i, t)]
                    prob += I[(i, t)] <= dem[(i, t)] + dict_data['M'] * (1 - y3[(i, t)])
                    #prob += I[(i, t)] == 0
        for i in items:
            prob += I[(i, 0)] == initial_inventory[i]

        for i in items:
            for t in range(0,dict_data['time_period']):
                # prob += dict_data['demand'][(i, t)] - I[(i, t)] <= dict_data['M'] * y2[(i, t)]
                # prob += I[(i, t)] - dict_data['demand'][(i, t)] <= dict_data['M'] * (1 - y2[(i, t)])

                prob += sold[(i, t)] <= I[(i, t)]
                prob += sold[(i, t)] <= dict_data['demand'][(i, t)]

                # prob += sold[(i, t)] >= I[(i, t)] - dict_data['M'] * (1 - y2[(i, t)])
                # prob += sold[(i, t)] >= dict_data['demand'][(i, t)] - dict_data['M'] * (y2[(i, t)])
        for j in suppliers:
            for t in time_period:
                for l in batch:
                    # https://math.stackexchange.com/questions/3380904/reformulating-constraint-containing-equivalence
                    M = dict_data['M']
                    m = -M
                    # batch limits
                    if l == 0:
                        c_min0 = 0
                        c_max0 = dict_data['u'][j][0]

                        prob += pulp.lpSum(O[(i, j, t)] for i in items) <= c_max0 + M * (1 - w[(j, l, t)])
                        prob += pulp.lpSum(O[(i, j, t)] for i in items) >= c_max0 + m * w[(j, l, t)]

                    # https://math.stackexchange.com/questions/3029175/question-to-the-solution-of-indicator-variable-if-x-is-in-specific-range?noredirect=1&lq=1

                    elif l == 1:
                        c_min1 = dict_data['u'][j][0]+1
                        c_max1 = dict_data['u'][j][1]
                        prob += pulp.lpSum(O[(i, j, t)] for i in items) <= c_min1 + M * delta[(j, l, t)] + M * w[
                            (j, l, t)]
                        prob += pulp.lpSum(O[(i, j, t)] for i in items) >= c_max1 - M * (1 - delta[(j, l, t)]) - M * w[
                            (j, l, t)]
                        prob += pulp.lpSum(O[(i, j, t)] for i in items) >= c_min1 - M * (1 - w[(j, l, t)])
                        prob += pulp.lpSum(O[(i, j, t)] for i in items) <= c_max1 + M * (1 - w[(j, l, t)])

                    elif l == 2:
                        c_min2 = dict_data['u'][j][1]+1
                        c_max2 = dict_data['u'][j][2]
                        prob += pulp.lpSum(O[(i, j, t)] for i in items) <= c_min2 + M * delta[(j, l, t)] + M * w[
                            (j, l, t)]
                        prob += pulp.lpSum(O[(i, j, t)] for i in items) >= c_max2 - M * (1 - delta[(j, l, t)]) - M * w[
                            (j, l, t)]
                        prob += pulp.lpSum(O[(i, j, t)] for i in items) >= c_min2 - M * (1 - w[(j, l, t)])
                        prob += pulp.lpSum(O[(i, j, t)] for i in items) <= c_max2 + M * (1 - w[(j, l, t)])

                    elif l == 3:
                        c_min3 = dict_data['u'][j][2]+1
                        c_max3 = dict_data['u'][j][3]
                        prob += pulp.lpSum(O[(i, j, t)] for i in items) <= c_min3 + M * w[(j, l, t)]
                        prob += pulp.lpSum(O[(i, j, t)] for i in items) >= c_min3 + m * (1 - w[(j, l, t)])
                # Associate appropriate discounts here: u1,u2...

                prob += discount[(j, t)] == (dict_data['discount_price'][j][0]*0.01*dict_data['fixed_costs'][j] * w[(j, 0, t)] +
                                             dict_data['discount_price'][j][1]*0.01*dict_data['fixed_costs'][j] * w[(j, 1, t)] +
                                             dict_data['discount_price'][j][2]*0.01*dict_data['fixed_costs'][j] * w[(j, 2, t)] +
                                             dict_data['discount_price'][j][3]*0.01*dict_data['fixed_costs'][j] * w[(j, 3, t)])


        for j in suppliers:
            for t in time_period:
                #pass
                # w(j,0,t)= 1 --> w(j,1,t)= 0 --> w(j,2,t)= 0
                prob += w[(j, 0, t)] <= 1 - w[(j, 1, t)]
                prob += w[(j, 0, t)] <= 1 - w[(j, 2, t)]
                prob += w[(j, 0, t)] <= 1 - w[(j, 3, t)]
                prob += w[(j, 1, t)] <= 1 - w[(j, 0, t)]
                prob += w[(j, 1, t)] <= 1 - w[(j, 2, t)]
                prob += w[(j, 1, t)] <= 1 - w[(j, 3, t)]
                prob += w[(j, 2, t)] <= 1 - w[(j, 0, t)]
                prob += w[(j, 2, t)] <= 1 - w[(j, 1, t)]
                prob += w[(j, 2, t)] <= 1 - w[(j, 3, t)]
                prob += w[(j, 3, t)] <= 1 - w[(j, 0, t)]
                prob += w[(j, 3, t)] <= 1 - w[(j, 1, t)]
                prob += w[(j, 3, t)] <= 1 - w[(j, 2, t)]


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

        # for v in sol:
           # print(v.name, "=", v.varValue)

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
