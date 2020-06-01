import time
import logging
# from pulp import *
import pulp


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
        suppliers=range(dict_data['num_suppliers'])
        time_period=range(dict_data['time_period'])
        #print(dict_data['costs'][14])
        problem_name = "shop ordering"
        prob = pulp.LpProblem(problem_name, pulp.LpMaximize)

        y = pulp.LpVariable.dicts(
            "y", [(j, t) for j in suppliers for t in time_period],
            cat=pulp.LpBinary
        )
        y2 = pulp.LpVariable.dicts(
            "y2", [(i, t) for i in items for t in time_period],
            cat=pulp.LpBinary
        )

        b = pulp.LpVariable.dicts(
            "b", [(i, t) for i in items for t in time_period], 0,
            cat=pulp.LpInteger
        )
        I = pulp.LpVariable.dicts("I", [(i,t) for i in items for t in time_period], lowBound=0, cat=pulp.LpInteger)

        sold = pulp.LpVariable.dicts(
            "sold", [(i, t) for i in items for t in time_period], 0,
            cat=pulp.LpInteger
        )

        O= pulp.LpVariable.dicts("O", [(i,j,t) for i in items for j in suppliers for t in time_period],0, cat = pulp.LpInteger)
        """
        prob += pulp.lpSum(min(dict_data['demand'][(i, t)], dict_data['inventory'][i])*dict_data['prices'][i] for i in items for t in time_period) -\
                pulp.lpSum(dict_data['fixed_costs'][j]*y[(j,t)] for j in suppliers for t in time_period) - \
                pulp.lpSum(dict_data['costs'][(i, j)]*O[(i,j,t)] for i in items for j in suppliers for t in time_period) - \
                pulp.lpSum(dict_data['extra_costs'][i]*b[(i,t)] for i in items for t in time_period) - \
                pulp.lpSum(dict_data['holding_costs'][i]*dict_data['inventory'][i] for i in items)
        """
        prob += pulp.lpSum(dict_data['prices'][i]*sold[(i,t)] for i in items for t in time_period) -\
                pulp.lpSum(dict_data['fixed_costs'][j] * y[(j, t)] for j in suppliers for t in time_period) - \
                pulp.lpSum(dict_data['costs'][(i,j)] * O[(i, j, t)] for i in items for j in suppliers for t in time_period) - \
                pulp.lpSum(dict_data['extra_costs'][i] * b[(i, t)] for i in items for t in time_period) - \
                pulp.lpSum(dict_data['holding_costs'][i] * I[(i,t)] for i in items for t in time_period)
                #pulp.lpSum([(dict_data['inventory'][(i, t - 1)] - dict_data['demand'][(i, t)] + sum([O[(i, j, t - dict_data['time_steps'][i] if t - dict_data['time_steps'][i] > 0 else 0)] for j in suppliers])) * dict_data['holding_costs'][i] for i in items for t in time_period])

        """
        for t in time_period:
            for i in items:
                prob += pulp.lpSum(O[(i,j,t)] for j in suppliers) == dict_data['demand'][(i,t)]
        """

        for j in suppliers:
            for t in time_period:
                prob += pulp.lpSum(O[i,j,t] for i in items) <= dict_data['M']*y[(j,t)]

        for i in items:
            for t in time_period:
                prob += b[(i, t)] >= (dict_data['demand'][(i, t)] - I[(i,t)])

        for i in items:
            prob += pulp.lpSum(I[i, 0]) == dict_data['inventory'][i]
            for t in time_period:
                if t!=0:
                    prob += pulp.lpSum(I[i,t]) == I[(i,t-1)] - dict_data['demand'][(i,t-1)] + pulp.lpSum(O[(i,j,t-dict_data['time_steps'][i] if t - dict_data['time_steps'][i] > 0 else 0)] for j in suppliers )

        """
        for i in items:
            for t in time_period:
                t=t - dict_data['time_steps'][i]
                if t<0:
                    t=0
                prob += dict_data['inventory'][i]== dict_data['inventory'][i] - dict_data['demand'][(i, t)]
        """
        for i in items:
            for t in time_period:
                prob += dict_data['demand'][(i, t)] - I[(i, t)] <= dict_data['M'] * y2[(i, t)]
                prob += I[(i, t)] - dict_data['demand'][(i, t)] <= dict_data['M'] * (1 - y2[(i, t)])

                prob += sold[(i, t)] <= I[(i, t)]
                prob += sold[(i, t)] <= dict_data['demand'][(i, t)]
                prob += sold[(i, t)] >= I[(i, t)] - dict_data['M']*(1 - y2[(i, t)])
                prob += sold[(i, t)] >= dict_data['demand'][(i, t)]- dict_data['M']*(y2[(i, t)])

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


        for v in sol:
            print (v.name, "=", v.varValue)

        print(pulp.LpStatus[prob.status])
        """

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
        """
        return of, sol, comp_time
