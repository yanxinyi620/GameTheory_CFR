#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :  rps.py
@Time    :  2021/11/13 00:02:31
@Author  :  yanxinyi
@Version :  v1.0
@Contact :  yanxinyi620@163.com
@Desc    :  A worked example of regret matching for the computation of a best 
            response strategy in Rock, Paper, Scissors (RPS).
'''

import random
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt 

try:
    from .base import BaseCFR
except:
    from base import BaseCFR


np.set_printoptions(suppress=True)


class RPSTrainer(BaseCFR):

    '''
    Demonstrate a worked example of regret matching for the computation of a best 
    response strategy in Rock, Paper, Scissors (RPS).
    '''

    def __init__(self, seed=None, *args, **kwargs):
        
        random.seed(seed)

        # Defining constants
        self.ROCK = 0
        self.PAPER = 1
        self.SCISSORS = 2
        self.NUM_ACTIONS = 3

        # Initializing variables
        self.my_regret = [0] * self.NUM_ACTIONS
        self.opp_regret = [0] * self.NUM_ACTIONS

        # Fixed opponent strategy
        self.fixed_strategy = [0.4, 0.3, 0.3]

        # Initializing cumulative containers
        self._my_strategies = []
        self.opp_strategies = []
        self.my_regrets = []
        self.opp_regrets = []

    def train(self, iterations, opp_fixed=False, plot=False):
        '''
        A Rock Paper Scissors trainer that utilizes regret matching in order to 
        approximately minimize expected regret over time.
        '''
        for _ in range(iterations):

            my_strategy = self._get_strategy(self.my_regret)
            opp_strategy = self._get_strategy(self.opp_regret) \
                           if not opp_fixed else self.fixed_strategy

            my_action = self._get_action(my_strategy)
            opp_action = self._get_action(opp_strategy)

            self.my_regret = self._action_regret(my_action, opp_action, self.my_regret)
            self.opp_regret = self._action_regret(opp_action, my_action, self.opp_regret)

            # Accumulate strategy and regret
            self._my_strategies.append(my_strategy)
            self.opp_strategies.append(opp_strategy)
            self.my_regrets.append(self.my_regret)
            self.opp_regrets.append(self.opp_regret)

        my_avg_strategies = self._get_avg_strategies(self.my_strategies)
        opp_avg_strategies = self._get_avg_strategies(self.opp_strategies)

        print('My (player1) average strategies:')
        df = pd.DataFrame(my_avg_strategies, columns=['Rock', 'Paper', 'Scissors'])
        print(df.iloc[range(0, iterations, int(iterations/10)), :])

        # Plotting average strategies
        if plot:
            self.avg_plot_strategies(my_avg_strategies, opp_avg_strategies)
            self.avg_plot_strategies(np.array(self.my_regrets), np.array(self.opp_regrets), 
                                     type='regrets')

        return my_avg_strategies, opp_avg_strategies, self.my_regrets, self.opp_regrets

    def _get_strategy(self, regret):
        '''Get current mixed strategy through regret-matching'''
        regret_pos = [max(i, 0) for i in regret]
        if sum(regret_pos) == 0:
            strategy = [1/self.NUM_ACTIONS] * self.NUM_ACTIONS
        else:
            strategy = [i/sum(regret_pos) for i in regret_pos]
        return strategy

    def _get_action(self, strategy):
        '''Get random action according to mixed-strategy distribution'''
        prob = random.uniform(0, 1)
        prob_sum = 0
        for action in range(self.NUM_ACTIONS):
            prob_sum += strategy[action]
            if prob <= prob_sum:
                break
        return action

    def _action_regret(self, action1, action2, regret):
        '''Compute action utilities'''
        utility = [0] * self.NUM_ACTIONS
        utility[action2] = 0  # tie
        utility[0 if action2 == (self.NUM_ACTIONS - 1) else action2 + 1] = 1  # win
        utility[self.NUM_ACTIONS - 1 if action2 == 0 else action2 - 1] = -1  # lose

        '''Accumulate action regrets'''
        regret = [regret[a] + utility[a] - utility[action1] for a in range(self.NUM_ACTIONS)]
        return regret

    def _get_avg_strategies(self, strategies):
        '''Get average mixed strategies across all training iterations'''
        avg_strategies = np.zeros(shape=[len(strategies), len(strategies[0])])
        avg_strategies[0] = np.array([strategies[0]])
        for i in range(1, len(strategies)):
            avg_strategies[i] = (avg_strategies[i-1]*i + strategies[i]) / (i+1)
        return avg_strategies

    @staticmethod
    def avg_plot_strategies(arr1, arr2, type='strategies', save_name=None):
        '''Plotting from average mixed strategies'''
        fig, (ax1, ax2) = plt.subplots(figsize=(10, 3), ncols=2)

        ax1.set_title("Convergence of player1's "+type)
        ax1.plot(arr1)
        ax1.legend(('Rock', 'Paper', 'Scissors'))

        ax2.set_title("Convergence of player2's "+type)
        ax2.plot(arr2)
        ax2.legend(('Rock', 'Paper', 'Scissors'))

        if save_name is not None:
            fig.savefig(save_name)
        plt.show()


if __name__=="__main__":
    rps = RPSTrainer(seed=1)
    my_avg_strategies, opp_avg_strategies, my_regrets, opp_regrets = rps.train(
        iterations=10000, opp_fixed=True, plot=True)
