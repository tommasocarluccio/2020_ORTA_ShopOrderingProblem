# -*- coding: utf-8 -*-
import logging
import numpy as np

np.random.seed(0)
class Instance():
    def __init__(self, sim_setting):
        """[summary]

        Arguments:
            sim_setting {[type]} -- [description]
        """
        logging.info("starting simulation...")
        # Number of time iterations
        self.time_period = sim_setting['time_period']
        self.M=sim_setting['M']

        # Initial inventory of the shop
        self.initial_inventory = np.around(np.random.uniform(
            sim_setting['min_init_product'],
            sim_setting['max_init_product'],
            sim_setting['num_products']
        ))
        self.initial_inventory = np.array(self.initial_inventory)
        self.inventory=np.zeros((sim_setting['time_period'],sim_setting['num_products']))
        self.inventory[0]=self.initial_inventory
        self.inventory=self.inventory.T

        # Demand for time_period days
        self.demand = []
        for i in range(self.time_period):
            self.demand.append(np.around(np.random.uniform(
                sim_setting['min_demand'],
                sim_setting['max_demand'],
                sim_setting['num_products']
            )))

        self.demand=np.array(self.demand)
        self.demand=self.demand.T

        # Prices of the items
        self.prices = np.around(np.random.uniform(
            sim_setting['min_price'],
            sim_setting['max_price'],
            sim_setting['num_products']
        ))
        # Time steps after which each item arrives
        self.time_steps = np.around(np.random.uniform(
            sim_setting['min_time_steps'],
            sim_setting['max_time_steps'],
            sim_setting['num_products']
        ))
        # List of suppliers with respective fixed costs
        self.fixed_costs = np.around(np.random.uniform(
            sim_setting['min_fixed_cost'],
            sim_setting['max_fixed_cost'],
            sim_setting['num_suppliers']
        ))
        # Matrix with suppliers in rows and costs in columns (num_suppliers)x(num_products)
        self.costs = np.zeros((sim_setting['num_suppliers'], sim_setting['num_products']))
        for i in range(sim_setting['num_suppliers']):
            for j in range(sim_setting['num_products']):
                self.costs[i] = (np.random.uniform(
                    sim_setting['min_cost'],
                    self.prices[i],
                    sim_setting['num_products']
                ))
                if np.random.rand(0, 1) > 0.8:
                   self.costs[i, j] = np.nan
        self.costs=self.costs.T


        """
        for i in range(sim_setting['num_suppliers']-1):
            self.costs[i]=(np.random.uniform(
                sim_setting['min_cost'],
                self.prices[i],
                sim_setting['num_products']
            ))
        # In this way not all suppliers have all products
        for i in range(1, sim_setting['num_suppliers']):
            for j in range(1, sim_setting['num_products']):
                # Supplier i has 0.8 probability of having product j
                if np.random.rand(0, 1) > 0.8:
                    self.costs[i][j] = np.nan
        """
        #print(self.costs[14])
        # Holding costs
        self.holding_costs = np.around(np.random.uniform(
            sim_setting['min_holding_cost'],
            sim_setting['max_holding_cost'],
            sim_setting['num_products']
        ))
        # Unsatisfied demand extracost
        self.extra_costs = np.around(np.random.uniform(
            sim_setting['min_extracost'],
            sim_setting['max_extracost'],
            sim_setting['num_products']
        ))

        self.num_products=sim_setting['num_products']
        self.num_suppliers = sim_setting['num_suppliers']
        logging.info("simulation end")

    def get_data(self):
        """[summary]

        Returns:
            [type] -- [description]
        """
        logging.info("getting data from instance...")
        return {
            "time_period": self.time_period,
            "inventory": self.inventory,
            "demand": self.demand,
            "prices": self.prices,
            "fixed_costs": self.fixed_costs,
            "costs": self.costs,
            "holding_costs": self.holding_costs,
            "extra_costs": self.extra_costs,
            "time_steps": self.time_steps,
            "num_products": self.num_products,
            "num_suppliers": self.num_suppliers,
            "M": self.M
        }
