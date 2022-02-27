#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :  dudo_1vs1.py
@Time    :  2021/11/01 00:21:53
@Author  :  yanxinyi
@Version :  v1.0
@Contact :  yanxinyi620@163.com
@Desc    :  Applying algorithm of Counterfactual Regret Minimization (with chance sampling) 
            to 1-Die-Versus-1-Die Dudo (limited to two 6-sided dice).
'''

if '':
    import random


    NUM_SIDES = 6
    NUM_ACTIONS = (2 * NUM_SIDES) + 1
    DUDO = NUM_ACTIONS - 1

    claimNum = [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2]
    claimRank = [2, 3, 4, 5, 6, 1, 2, 3, 4, 5, 6, 1]

    allClaimed = ['1*2', '1*3', '1*4', '1*5', '1*6', '1*1',
                '2*2', '2*3', '2*4', '2*5', '2*6', '2*1']
    all_actions = allClaimed + ['Dudo']


    def get_isClaimed(action):
        isClaimed = [0] * len(allClaimed)
        for i in range(len(allClaimed)):
            if allClaimed[i] in action:
                isClaimed[i] = 1
        return isClaimed


    def claimHistoryToString(isClaimed):
        sb = []
        for a in range(NUM_ACTIONS-1):
            if isClaimed[a]:
                # if len(sb) > 0:
                #     sb.append(str(claimNum[a]) + '*' + str(claimRank[a]))
                sb.append(str(claimNum[a]) + '*' + str(claimRank[a]))
        return ', '.join(sb)


    def infoSetToInteger(playerRoll, isClaimed):
        infoSetNum = playerRoll
        for a in range(NUM_ACTIONS - 2, -1, -1):
            infoSetNum = 2 * infoSetNum + (1 if isClaimed[a] else 0)
        return infoSetNum


    class DudoUtilities(object):

        def __init__(self):
            isClaimed = get_isClaimed(['1*3', '1*6', '2*6', 'Dudo'])
            ClaimedString = claimHistoryToString(isClaimed)
            print(ClaimedString)

            playerRoll = 1
            infoSetNum = infoSetToInteger(playerRoll, isClaimed)
            print(infoSetNum)


# ----------------------------------------------------
import random


NUM_SIDES = 6
NUM_ACTIONS = (2 * NUM_SIDES) + 1
# DUDO = NUM_ACTIONS - 1

# claimNum = [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2]
# claimRank = [2, 3, 4, 5, 6, 1, 2, 3, 4, 5, 6, 1]

# allClaimed = ['1*2', '1*3', '1*4', '1*5', '1*6', '1*1',
#               '2*2', '2*3', '2*4', '2*5', '2*6', '2*1']
# all_actions = allClaimed + ['Dudo']

node_map = {}


class Node(object):
    '''
    Information set node class definition
    '''
    def __init__(self, *args, **kwargs):
        '''Kuhn node definitions'''
        self.info_set = ''
        self.regret_sum = [0] * NUM_ACTIONS
        self.strategy = [0] * NUM_ACTIONS
        self.strategy_sum = [0] * NUM_ACTIONS

    def get_strategy(self, realization_weight):
        '''Get current information set mixed strategy through regret-matching'''
        normalizing_sum = 0
        for a in range(NUM_ACTIONS):
            self.strategy[a] = max(self.regret_sum[a], 0)
            normalizing_sum += self.strategy[a]
        
        for a in range(NUM_ACTIONS):
            if normalizing_sum > 0:
                self.strategy[a] /= normalizing_sum
            else:
                self.strategy[a] = 1 / NUM_ACTIONS
            self.strategy_sum[a] += realization_weight * self.strategy[a]
        
        return self.strategy

    def average_strategy(self):
        '''Get average information set mixed strategy across all training iterations'''
        avg_strategy = [0] * NUM_ACTIONS
        normalizing_sum = 0

        for a in range(NUM_ACTIONS):
            normalizing_sum += self.strategy_sum[a]

        for a in range(NUM_ACTIONS):       
            if normalizing_sum > 0:
                avg_strategy[a] = self.strategy_sum[a] / normalizing_sum
            else:
                avg_strategy[a] = 1 / NUM_ACTIONS
        
        return avg_strategy


class DudoTrainer(object):
    '''
    DudoTrainer main method
    '''
    def __init__(self, seed=None, *args, **kwargs):
        
        random.seed(seed)

    def train(self, iterations):
        '''Train Kuhn poker'''
        util = 0
        for i in range(iterations):
            side1 = random.randint(1, NUM_SIDES)
            side2 = random.randint(1, NUM_SIDES)
            util += self.cfr([side1, side2], '', 1, 1, i)

        print("Average game value:", util/iterations)

    def cfr(self, sides, history, p0, p1, iter):
        '''Counterfactual regret minimization iteration'''
        plays = len(history)
        player = plays % 2
        opponent = 1 - player

        info_set = str(sides[player]) + history
        node = self._infoset_node(info_set)
        strategy = node.get_strategy(p0 if player == 0 else p1) ???

        payoff = self._terminal_payoff(plays, history, sides, player, opponent)


    @staticmethod
    def _infoset_node(info_set):
        '''Get information set node or create it if nonexistant'''
        if info_set not in node_map:
            node = Node()
            node.info_set = info_set
            node_map[info_set] = node
        node = node_map[info_set]
        return node

