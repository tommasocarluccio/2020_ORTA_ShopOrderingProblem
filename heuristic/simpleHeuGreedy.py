# -*- coding: utf-8 -*-
import time
import math
import logging
import pulp
import numpy as np

# Solve the problem using a Greedy algorithm which chooses the best option day by day
class SimpleHeuGreedy():
    def __init__(self):
        pass

    def solveGreedy(
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
        batch=[0, 1, 2, 3]
        initial_inventory=dict_data['initial_inventory']
        pre_order=dict_data['pre_order']

        sol_o = np.zeros((dict_data['num_products'], dict_data['time_period']))
        of_tot=0
        time_tot=0

        # Initialize inventory
        I= initial_inventory
        for t in time_period:

            # Define problem
            problem_name = "shop ordering"
            prob = pulp.LpProblem(problem_name, pulp.LpMaximize)  # maximize profit

            #Set of variables:

            # y is binary variable that is 1 if a order to the supplier j at time t is performed
            y = pulp.LpVariable.dicts("y", [(j) for j in suppliers], cat=pulp.LpBinary)

            # y2 is a auxiliary binary variable to linearize minimum function (between inventory and demand of product i at time t)
            y2 = pulp.LpVariable.dicts("y2", [(i) for i in items], cat=pulp.LpBinary)

            # integer variable concerning the extra-cost due to unsatisfied demand
            b = pulp.LpVariable.dicts("b", [(i) for i in items], 0, cat=pulp.LpInteger)

            # variable to compute the minimum between inventory and demand, i.e. the amount of product i sold at time t
            sold = pulp.LpVariable.dicts("sold", [(i) for i in items],cat=pulp.LpInteger)
            
            # order for product i for each time t
            O = pulp.LpVariable.dicts("O", [(i, j) for i in items for j in suppliers], 0, cat=pulp.LpInteger)

            # Discount function
            discount= pulp.LpVariable.dicts("discount", [(j) for j in suppliers],lowBound=0, cat=pulp.LpContinuous)

            # Needed for discount
            w = pulp.LpVariable.dicts("w", [(j,l) for j in suppliers for l in batch], cat=pulp.LpBinary)

            # Needed for "Heuristic Constraint 1"
            #k = pulp.LpVariable.dicts("k", [(i) for i in items], cat=pulp.LpBinary)

            # Needed for constraint: https://math.stackexchange.com/questions/3029175/question-to-the-solution-of-indicator-variable-if-x-is-in-specific-range?noredirect=1&lq=1
            delta = pulp.LpVariable.dicts("delta", [(j,l) for j in suppliers for l in batch], cat=pulp.LpBinary)

            # Objective function:
            prob += pulp.lpSum(dict_data['prices'][i] * sold[(i)] for i in items)-\
                    pulp.lpSum(dict_data['fixed_costs'][j] * y[(j)] for j in suppliers) - \
                    pulp.lpSum(dict_data['costs'][(i, j)] * O[(i, j)] for i in items for j in suppliers) - \
                    pulp.lpSum(dict_data['extra_costs'][i] * b[(i)] for i in items) - \
                    pulp.lpSum(dict_data['holding_costs'][i] * I[(i)] for i in items) + \
                    pulp.lpSum(discount[(j)] for j in suppliers)

            # Set of constraints:

            # Constraint 1
            for j in suppliers:
                prob += pulp.lpSum(O[i, j] for i in items) <= dict_data['M'] * y[(j)]

            # Constraint 2
            for i in items:
                prob += b[(i)] >= (dict_data['demand'][(i, t)] - I[(i)])

            # Constraint 3
            for i in items:
                prob += sold[(i)] <= I[(i)]
                prob += sold[(i)] <= dict_data['demand'][(i, t)]
            
            # Discount function
            for j in suppliers:
                for l in batch:
                    # https://math.stackexchange.com/questions/3380904/reformulating-constraint-containing-equivalence
                    M = dict_data['M']
                    m = -M
                    # batch limits
                    if l == 0:
                        c_min0 = 0
                        c_max0 = dict_data['u'][j][0]
                        prob += pulp.lpSum(O[(i, j)] for i in items) <= c_max0 + M * (1 - w[(j, l)])
                        prob += pulp.lpSum(O[(i, j)] for i in items) >= c_max0 + m * w[(j, l)]

                        # https://math.stackexchange.com/questions/3029175/question-to-the-solution-of-indicator-variable-if-x-is-in-specific-range?noredirect=1&lq=1

                    elif l == 1:
                        c_min1 = dict_data['u'][j][0]+1
                        c_max1 = dict_data['u'][j][1]
                        prob += pulp.lpSum(O[(i, j)] for i in items) <= c_min1 + M * delta[(j, l)] + M * w[(j, l)]
                        prob += pulp.lpSum(O[(i, j)] for i in items) >= c_max1 - M * (1 - delta[(j, l)]) - M * w[(j, l)]
                        prob += pulp.lpSum(O[(i, j)] for i in items) >= c_min1 - M * (1 - w[(j, l)])
                        prob += pulp.lpSum(O[(i, j)] for i in items) <= c_max1 + M * (1 - w[(j, l)])

                    elif l == 2:
                        c_min2 = dict_data['u'][j][1]+1
                        c_max2 = dict_data['u'][j][2]
                        prob += pulp.lpSum(O[(i, j)] for i in items) <= c_min2 + M * delta[(j, l)] + M * w[(j, l)]
                        prob += pulp.lpSum(O[(i, j)] for i in items) >= c_max2 - M * (1 - delta[(j, l)]) - M * w[(j, l)]
                        prob += pulp.lpSum(O[(i, j)] for i in items) >= c_min2 - M * (1 - w[(j, l)])
                        prob += pulp.lpSum(O[(i, j)] for i in items) <= c_max2 + M * (1 - w[(j, l)])

                    elif l == 3:
                        c_min3 = dict_data['u'][j][2]+1
                        #c_max3 = dict_data['u'][j][3]
                        prob += pulp.lpSum(O[(i, j)] for i in items) <= c_min3 + M * w[(j, l)]
                        prob += pulp.lpSum(O[(i, j)] for i in items) >= c_min3 + m * (1 - w[(j, l)])

                
                # Associate appropriate discounts here: u1,u2...
                prob += discount[(j)] == (dict_data['discount_price'][j][0]*0.01*dict_data['fixed_costs'][j] * w[(j, 0)] +
                                          dict_data['discount_price'][j][1]*0.01*dict_data['fixed_costs'][j] * w[(j, 1)] +
                                          dict_data['discount_price'][j][2]*0.01*dict_data['fixed_costs'][j] * w[(j, 2)] +
                                          dict_data['discount_price'][j][3]*0.01*dict_data['fixed_costs'][j] * w[(j, 3)])

            for j in suppliers:
                # w(j,0,t)= 1 --> w(j,1,t)= 0 --> w(j,2,t)= 0
                prob += w[(j, 0)] <= 1 - w[(j, 1)]
                prob += w[(j, 0)] <= 1 - w[(j, 2)]
                prob += w[(j, 0)] <= 1 - w[(j, 3)]
                prob += w[(j, 1)] <= 1 - w[(j, 0)]
                prob += w[(j, 1)] <= 1 - w[(j, 2)]
                prob += w[(j, 1)] <= 1 - w[(j, 3)]
                prob += w[(j, 2)] <= 1 - w[(j, 0)]
                prob += w[(j, 2)] <= 1 - w[(j, 1)]
                prob += w[(j, 2)] <= 1 - w[(j, 3)]
                prob += w[(j, 3)] <= 1 - w[(j, 0)]
                prob += w[(j, 3)] <= 1 - w[(j, 1)]
                prob += w[(j, 3)] <= 1 - w[(j, 2)]

            # Heuristic Constraint 1: Order only if I[(i, t)] <= threshold
            for i in items:
                threshold=100 # OPTIMIZE THIS THRESHOLD
                if I[(i)] <= threshold:
                    prob += pulp.lpSum(O[(i, j)] for j in suppliers) == dict_data['demand'][(i, t)]
                else:
                    prob += pulp.lpSum(O[(i, j)] for j in suppliers) == 0

                #M=dict_data['M']
                #m=-M
                #prob += M*(1-k[(i)]) >= - threshold + I[(i)]
                #prob += m*k[(i)] <= - threshold + I[(i)]
                # How much to order??? - Modify the constraint!!!
                #prob += pulp.lpSum(O[(i, j)] for j in suppliers) == dict_data['demand'][(i, t)]*k[(i)] # Order as much as the demand

            # Solve the problem using COIN_CMD solver
            msg_val = 1 if verbose else 0
            start = time.time()
            solver = pulp.solvers.COIN_CMD(msg=msg_val, maxSeconds=time_limit, fracGap=gap)
            solver.solve(prob)
            end = time.time()

            # Update log file
            logging.info("\t Status: {}".format(pulp.LpStatus[prob.status]))

            # Solution of the problem
            sol = prob.variables()
            of = pulp.value(prob.objective) # Profit from objective function
            comp_time = end - start

            # print the values of the variables of the solution
            for v in sol:
               print(v.name, "=", v.varValue)

            # Status of the solution (infesible, optimal...)
            print(pulp.LpStatus[prob.status])

            # Compute O[(i,j)] as a matrix sol_o[i,t] per item and time_step
            for i in items:
                result = 0
                for j in suppliers:
                    result += pulp.value(O[(i, j)])
                sol_o[(i, t)] = result

            # Print the values of O[(i, j)]
            #for i in items:
                #for j in suppliers:
                    #print(pulp.value(O[(i, j)]))

            # Print partial solution
            print(of, sol_o)

            for var in sol:
                logging.info("{} {}".format(var.name, var.varValue))
                if "O_" in var.name:
                    pass
                    # sol_o[int(var.name.replace("O_", ""))] = abs(var.varValue)

            logging.info("\n\tof: {}\n\tsol:\n{} \n\ttime:{}".format(of, sol_o, comp_time))
            logging.info("#########")

            # Update the inventory
            for i in items:
                if t-int(dict_data['time_steps'][i]) < 0:
                    dem = I[(i)] - pulp.value(sold[(i)]) + pre_order[(i, t-int(dict_data['time_steps'][i]))]
                    if dem > 0:
                        I[(i)]=dem
                    else:
                        I[(i)]=0
                else:
                    dem = I[(i)] - pulp.value(sold[(i)]) + sol_o[(i, t-int(dict_data['time_steps'][i]))]
                    if dem > 0:
                        I[(i)]=dem
                    else:
                        I[(i)]=0
            print(I)

            # Sum of the profits from the different time steps
            of_tot += of
            time_tot += comp_time

        return of_tot, sol_o, time_tot
