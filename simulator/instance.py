import logging
import numpy as np
import random

np.random.seed(0)
random.seed(0)
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
        self.M2 = sim_setting['M2']

        # Initial inventory of the shop
        self.initial_inventory = np.around(np.random.uniform(
            sim_setting['min_init_product'],
            sim_setting['max_init_product'],
            sim_setting['num_products']
        ))
        print(self.initial_inventory)
        #self.initial_inventory = np.array(self.initial_inventory)
        #self.inventory=np.zeros((sim_setting['time_period'],sim_setting['num_products']))
        #self.inventory[0]=self.initial_inventory
        self.initial_inventory=self.initial_inventory.T

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
        print(self.demand)
        #self.pre_order=np.zeros((sim_setting['num_products'], sim_setting['max_time_steps']))
        self.pre_order = []
        #np.random.seed(1)
        for i in range(self.time_period):
            self.pre_order.append(np.around(np.random.uniform(
                sim_setting['min_pre_order'],
                sim_setting['max_pre_order'],
                sim_setting['num_products']
            )))
        self.pre_order = np.array(self.pre_order)
        self.pre_order = self.pre_order.T
        #print(self.pre_order)
        self.inventory = np.zeros((sim_setting['num_products'], sim_setting['max_time_steps']))


        # Prices of the items
        self.prices = np.around(np.random.uniform(
            sim_setting['min_price'],
            sim_setting['max_price'],
            sim_setting['num_products']
        ))
        print(self.prices)
        # Time steps after which each item arrives
        self.time_steps = np.around(np.random.uniform(
            sim_setting['min_time_steps'],
            sim_setting['max_time_steps'],
            sim_setting['num_products']
        ))
        # List of suppliers with respective fixed costs
        """
        self.fixed_costs = np.around(np.random.uniform(
            sim_setting['min_fixed_cost'],
            sim_setting['max_fixed_cost'],
            sim_setting['num_suppliers']
        ))
        """
        self.fixed_costs=[1,5000,3000]
        self.fixed_costs=np.array(self.fixed_costs)
        # Matrix with suppliers in rows and costs in columns (num_suppliers)x(num_products)
        self.costs = np.zeros((sim_setting['num_suppliers'], sim_setting['num_products']))
        for i in range(sim_setting['num_suppliers']):
            for j in range(sim_setting['num_products']):
                self.costs[i] = (np.random.uniform(
                    sim_setting['min_cost'],
                    self.prices[j],
                    sim_setting['num_products']
                ))
        for i in range(sim_setting['num_suppliers']):
            for j in range(sim_setting['num_products']):
                if random.random()> 0.9:
                   self.costs[i, j] = 1000000  # In order to avoid NaN (would never choose this item: too costly)


        self.costs=self.costs.T
        #print(self.costs)


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

        self.discount=[]
        for i in range(sim_setting['num_suppliers']):

            #c1l=0
            #c1h= random.randint(10,20)
            u1=random.randint(1,5)
            #c2l=c1h
            #c2h=random.randint(c2l,c2l+15)
            u2=random.randint(10,15)
            #c3l=c2h
            #c3h=random.randint(c3l,c3l+20)
            u3=random.randint(15, 20)
            a = [u1,u2,u3]
            self.discount.append(a)
        self.discount = np.array(self.discount)
        print(self.discount)


        self.num_products=sim_setting['num_products']
        self.num_suppliers = sim_setting['num_suppliers']
        self.max_time_steps=sim_setting['max_time_steps']
        logging.info("simulation end")

    def get_data(self):
        """[summary]

        Returns:
            [type] -- [description]
        """
        logging.info("getting data from instance...")
        return {
            "time_period": self.time_period,
            "initial_inventory": self.initial_inventory,
            "demand": self.demand,
            "prices": self.prices,
            "fixed_costs": self.fixed_costs,
            "costs": self.costs,
            "holding_costs": self.holding_costs,
            "extra_costs": self.extra_costs,
            "time_steps": self.time_steps,
            "num_products": self.num_products,
            "num_suppliers": self.num_suppliers,
            "max_time_steps": self.max_time_steps,
            "M": self.M,
            "pre_order": self.pre_order,
            "M2": self.M2,
            "discount":self.discount,
            "Inventory_new": self.inventory

        }
