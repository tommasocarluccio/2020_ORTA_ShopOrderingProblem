# -*- coding: utf-8 -*-
import logging
import numpy as np


class Instance():
    def __init__(self, sim_setting):
        """[summary]
        
        Arguments:
            sim_setting {[type]} -- [description]
        """
        logging.info("starting simulation...")
        self.max_size = sim_setting['knapsack_size']
        self.sizes = np.around(np.random.uniform(
            sim_setting['low_size'],
            sim_setting['high_size'],
            sim_setting['n_items']
        ))
        self.profits = np.around(np.random.uniform(
            sim_setting['low_profit'],
            sim_setting['high_profit'],
            sim_setting['n_items']
        ))
        self.n_items = sim_setting['n_items']
        logging.info("simulation end")

    def get_data(self):
        """[summary]
        
        Returns:
            [type] -- [description]
        """
        logging.info("getting data from instance...")
        return {
            "profits": self.profits,
            "sizes": self.sizes,
            "max_size": self.max_size,
            "n_items": self.n_items
        }
