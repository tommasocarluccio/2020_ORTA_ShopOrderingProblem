# -*- coding: utf-8 -*-
import time
import logging
import pulp
import numpy as np
import matplotlib.pyplot as plt


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

        # Define constants
        logging.info("#########")
        items = range(dict_data['num_products'])
        suppliers = range(dict_data['num_suppliers'])
        time_period = range(dict_data['time_period'])
        batch = [0, 1, 2, 3]
        initial_inventory = dict_data['initial_inventory']
        pre_order = dict_data['pre_order']

        # Define problem
        problem_name = "shop ordering"
        prob = pulp.LpProblem(problem_name, pulp.LpMaximize)  # maximize profit

        # Define the LP variables:

        # y is binary variable that is 1 if a order to the supplier j at time t is performed
        y = pulp.LpVariable.dicts("y", [(j, t) for j in suppliers for t in time_period],cat=pulp.LpBinary)

        # y2 is a auxiliary binary variable to linearize minimum function (between inventory and demand of product i at time t)
        y2 = pulp.LpVariable.dicts("y2", [(i, t) for i in items for t in time_period],cat=pulp.LpBinary)

        # integer variable concerning the extra-cost due to unsatisfied demand
        b = pulp.LpVariable.dicts("b", [(i, t) for i in items for t in time_period], 0,cat=pulp.LpInteger)

        # w is binary variable to linearize discount function
        w = pulp.LpVariable.dicts("w", [(j, l, t) for j in suppliers for l in batch for t in time_period],0,cat=pulp.LpBinary)

        # Needed for constraint: https://math.stackexchange.com/questions/3029175/question-to-the-solution-of-indicator-variable-if-x-is-in-specific-range?noredirect=1&lq=1
        delta = pulp.LpVariable.dicts("delta", [(j, l, t) for j in suppliers for l in batch for t in time_period],0,cat=pulp.LpBinary)

        # inventory for each product i at time t, depending on inventory of t-1, demand and arrived orders
        I= pulp.LpVariable.dicts("I", [(i, t) for i in items for t in time_period], 0, cat=pulp.LpInteger)

        # quantity of each item sold at time t (minimum between demand and inventory)
        sold = pulp.LpVariable.dicts("sold", [(i, t) for i in items for t in time_period], 0, cat=pulp.LpInteger)

        # discount applied by supplier j at time t
        discount = pulp.LpVariable.dicts("discount", [(j, t) for j in suppliers for t in time_period], lowBound=0,cat=pulp.LpContinuous)

        # order for product i for each time t
        O = pulp.LpVariable.dicts("O", [(i, j, t) for i in items for j in suppliers for t in time_period], 0, cat=pulp.LpInteger)

        # Objective function:

        prob += pulp.lpSum(dict_data['prices'][i] * sold[(i, t)] for i in items for t in range(0,dict_data['time_period'])) -\
                pulp.lpSum(dict_data['fixed_costs'][j] * y[(j, t)] for j in suppliers for t in time_period) - \
                pulp.lpSum(dict_data['costs'][(i, j)] * O[(i, j, t)] for i in items for j in suppliers for t in time_period) - \
                pulp.lpSum(dict_data['extra_costs'][i] * b[(i, t)] for i in items for t in range(0, dict_data['time_period'])) - \
                pulp.lpSum(dict_data['holding_costs'][i] * I[(i, t)] for i in items for t in range(0, dict_data['time_period'])) + \
                pulp.lpSum(discount[(j, t)] for j in suppliers for t in time_period)

        # Set of constraints:

        # Constraint 1
        for j in suppliers:
            for t in range(0, dict_data['time_period']):
                prob += pulp.lpSum(O[i, j, t] for i in items) <= dict_data['M'] * y[(j, t)]

        # Constraint 2
        for i in items:
            for t in time_period:
                prob += b[(i, t)] >= (dict_data['demand'][(i, t)] - I[(i, t)])

        # Constraint 3
        for i in items:
            for t in range(1,dict_data['time_period']):
                if t-int(dict_data['time_steps'][i]) < 0:
                    prob += I[(i, t)] == (I[(i, t-1)] - sold[(i, t-1)] + pre_order[(i, -1-(t - int(dict_data['time_steps'][i])))]) 
                else:
                    prob += I[(i, t)] == I[(i, t-1)] - sold[(i, t-1)] + pulp.lpSum(O[(i, j, t-int(dict_data['time_steps'][i]))] for j in suppliers)

        # Constraint 4
        for i in items:
            prob += I[(i, 0)] == initial_inventory[i]

        # Constraint 5
        for i in items:
            for t in range(0,dict_data['time_period']):
                prob += sold[(i, t)] <= I[(i, t)]
                prob += sold[(i, t)] <= dict_data['demand'][(i, t)]

        # Discount function
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

                prob += discount[(j, t)] == (dict_data['discount_price'][j][0]*0.01*dict_data['fixed_costs'][j] * w[(j, 0, t)] +
                                             dict_data['discount_price'][j][1]*0.01*dict_data['fixed_costs'][j] * w[(j, 1, t)] +
                                             dict_data['discount_price'][j][2]*0.01*dict_data['fixed_costs'][j] * w[(j, 2, t)] +
                                             dict_data['discount_price'][j][3]*0.01*dict_data['fixed_costs'][j] * w[(j, 3, t)])

        for j in suppliers:
            for t in time_period:
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


        # Solve the problem using CBC solver
        msg_val = 1 if verbose else 0
        start = time.time()
        solver = pulp.solvers.COIN_CMD(msg=msg_val,maxSeconds=time_limit,fracGap=gap)
        solver.solve(prob)
        end = time.time()

        # Update log
        logging.info("\t Status: {}".format(pulp.LpStatus[prob.status]))

        # Solution variables
        sol = prob.variables()
        of = pulp.value(prob.objective)
        comp_time = end - start

        # Print all variables of the problem
        #for v in sol:
           #print(v.name, "=", v.varValue)

        # Print status of the problem
        print(pulp.LpStatus[prob.status])

        # Put solution in matrix for export (return simulation results as arrays)
        sol_o = np.zeros((dict_data['num_products'], dict_data['time_period']))
        for t in range(0,dict_data['time_period']):
            for i in items:
                result = 0
                for j in suppliers:
                    result += pulp.value(O[(i, j, t)])
                sol_o[(i, t)] = result

        sol_supp = np.zeros((dict_data['num_suppliers']))
        for j in suppliers:
            result = 0
            for t in range(0,dict_data['time_period']):
                for i in items:
                    result += pulp.value(O[(i, j, t)])
                sol_supp[(j)] = result

        sol_y = np.zeros((dict_data['num_suppliers'], dict_data['time_period']))
        for j in suppliers:
            for t in time_period:
                sol_y[(j, t)] = pulp.value(y[(j,t)])

        sol_discount = np.zeros((dict_data['num_suppliers'], dict_data['time_period']))
        for j in suppliers:
            for t in time_period:
                sol_discount[(j, t)] = pulp.value(discount[(j,t)])

        sol_O_with_j = np.zeros((dict_data['num_products'], dict_data["num_suppliers"], dict_data['time_period']))
        for i in items:
            for j in suppliers:
                for t in time_period:
                    sol_O_with_j[(i,j, t)] = pulp.value(O[(i,j,t)])

        sol_I = np.zeros((dict_data['num_products'], dict_data['time_period']))
        for i in items:
            for t in time_period:
                sol_I[(i, t)] = pulp.value(I[(i,t)])

        sol_sold = np.zeros((dict_data['num_products'], dict_data['time_period']))
        for i in items:
            for t in time_period:
                sol_sold[(i, t)] = pulp.value(sold[(i,t)])


        # Add variables to the log
        for var in sol:
            logging.info("{} {}".format(var.name, var.varValue))

            if "O_" in var.name:
                pass
                # sol_o[int(var.name.replace("O_", ""))] = abs(var.varValue)
        logging.info("\n\tof: {}\n\tsol:\n{} \n\t time:{}".format(of, sol_o, comp_time))
        logging.info("#########")


        return of, sol_o, comp_time, sol_y, sol_discount, sol_O_with_j



    def compareDemand(
        self, of_exact, dict_data, sol_y, sol_discount, sol_o, sol_O_with_j, moreDemand,
        time_limit=None,gap=None, verbose=False
    ):

        """
        This function calculates the effect of an over/under estimation of the demand.
        The input parameters mast be the results of the simulation, the dict_data of the instance, 
        and the array moreDemand, which contains the values to be added to the demand.
        This function prints in a graph the difference between the profit obtained with the expected demand
        and the profit actually obtained with the modified demand
        """

        # Define the variables
        items = range(dict_data['num_products'])
        suppliers = range(dict_data['num_suppliers'])
        time_period = range(dict_data['time_period'])
        initial_inventory = dict_data['initial_inventory']
        pre_order = dict_data['pre_order']

        # Define the initial inventory for all the simulations
        num_moreDemand = int(moreDemand.shape[0])
        initial_inventory = np.zeros((dict_data['num_products'],num_moreDemand))
        for k in range(num_moreDemand):
            initial_inventory[:,k] = dict_data['initial_inventory']


        difference=[]
        k=0
        # Each step calculates the profit with a different demand 
        for m in moreDemand:

            # Initialize inventory
            overI=initial_inventory[:,k]
            print(initial_inventory[:,k])

            # Increase/decrease demand
            overDemand = dict_data['demand'] + m
            for i in items:
                for t in time_period:
                    if overDemand[(i,t)] < 0:
                        overDemand[(i,t)] = 0

            # Print the new demand
            print("overDemand:")
            print(overDemand)

            # Pay the costs related to the order (not influenced by the demand)
            overProfit=0
            for t in time_period:
                for j in suppliers:
                    overProfit += - dict_data['fixed_costs'][j] * sol_y[(j, t)]
                    overProfit += sol_discount[(j, t)]

            for i in items:
                for j in suppliers:
                    for t in time_period:
                        overProfit += - dict_data['costs'][(i, j)] * sol_O_with_j[(i, j, t)]

            # Calculate profit due to new demand (requires updating inventory differently from the optimal solution)
            over_b=0
            overSold=np.zeros(dict_data["num_products"]) # Items sold wrt new demand
            for t in time_period:
                for i in items:
                    if t != 0:
                        # Update the inventory
                        if t-int(dict_data['time_steps'][i]) < 0:
                            # Take instance preorder value from pre-order table
                            dem = overI[(i)] - overSold[(i)] + pre_order[(i, -1-(t-int(dict_data['time_steps'][i])))] 
                            # Avoid negative inventory
                            if dem > 0:
                                overI[(i)]=dem
                            else:
                                overI[(i)]=0
                        else:
                            dem = overI[(i)] - overSold[(i)] + sol_o[(i, t-int(dict_data['time_steps'][i]))]
                            if dem > 0:
                                overI[(i)]=dem
                            else:
                                overI[(i)]=0

                    # instanciate b 
                    if (overDemand[(i, t)] - overI[(i)]) > 0:
                        over_b=(overDemand[(i, t)] - overI[(i)])
                    else:
                        over_b=0

                    # Subtract extracosts and holding costs (require inventory)
                    overProfit += - dict_data['extra_costs'][i] * over_b
                    overProfit += - dict_data['holding_costs'][i] * overI[(i)]

                    # Add to the profit the ravenue by the selling of products with new demand
                    overSold[(i)]=0
                    if overDemand[(i, t)] >= overI[(i)]:
                        overProfit += dict_data['prices'][i] * overI[(i)]
                        overSold[(i)] = overI[(i)]
                    else:
                        overProfit += dict_data['prices'][i] * overDemand[(i, t)]
                        overSold[(i)] = overDemand[(i, t)]

            print("The profit obtained with the demand + ", m, " is equal to:")
            print(overProfit)
            difference.append(overProfit - of_exact)
            k += 1

        # Plot the difference between over/under demand and optimal 
        plt.plot(moreDemand, difference, 'r')
        plt.xlabel('Value added to the optimal demand')
        plt.ylabel('Profit difference')
        plt.title('Profit difference between over/under estimated and optimal demand')
        plt.grid(True)
        plt.show()

