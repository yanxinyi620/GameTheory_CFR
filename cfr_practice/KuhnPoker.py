#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :  KuhnPoker.py
@Time    :  2021/11/14 23:11:35
@Author  :  yanxinyi
@Version :  v1.0
@Contact :  yanxinyi620@163.com
@Desc    :  Applying algorithm of Counterfactual Regret Minimization (with chance sampling) 
            to Kuhn Poker.

java code structure:
    class Node {
        <Kuhn node definitions>
        <Get current information set mixed strategy through regret-matching>
        <Get average information set mixed strategy across all training iterations>
        <Get information set string representation>
    }

    class KuhnTrainer {
        <Kuhn Poker definitions>
        <Information set node class definition>
        <Train Kuhn poker>
        <Counterfactual regret minimization iteration>
        <KuhnTrainer main method>
    }

    <Counterfactual regret minimization iteration>≡
    private double cfr(int[] cards, String history, double p0, double p1) {
        int plays = history.length();
        int player = plays % 2;
        int opponent = 1 - player;
        <Return payoff for terminal states>
        String infoSet = cards[player] + history;
        <Get information set node or create it if nonexistant>
        <For each action, recursively call cfr with additional history and probability>
        <For each action, compute and accumulate counterfactual regret>
        return nodeUtil;
    }
'''

import logging
import random


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')


# Kuhn Poker definitions
PASS = 0
BET = 1
NUM_ACTIONS = 2
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

    def toString(self):
        '''
        Get information set string representation

        print(
            '{0:4s}'.format(self.info_set) + ': [' + 
            ', '.join(str(x) for x in self.average_strategy()) + ']'
            )
        print(
            f'{self.info_set:4s}: [' + 
            f', '.join(str("%.2f" % x) for x in self.average_strategy()) + 
            f']'
            )
        '''
        return f'{self.info_set:4s}: [' + \
               f', '.join('%.3g' % float(('%.2f' % x)) for x in self.average_strategy()) + f']'


class KuhnTrainer(object):
    '''
    KuhnTrainer main method
    '''
    def __init__(self, seed=None, *args, **kwargs):
        
        random.seed(seed)

    def train(self, iterations):
        '''Train Kuhn poker'''
        cards = [1,2,3]
        util = 0

        for i in range(iterations):
            random.shuffle(cards)
            if i == 0 or (i+1) % 10000 == 0:
                logging.info(f'[iter: {i+1}] cards: {cards}\n')
                logging.info(f'iter\thistory\tp0\tp1\t'
                             f'plays\tplayer\topponent\t'
                             f'info_set\tstrategy\tpayoff\t'
                             f'next_history\tutil\tnode_util\tregret')
            
            util += self.cfr(cards, '', 1, 1, i)
            if i == 0 or (i+1) % 1000 == 0:
                logging.info(f'[iter: {i+1}] avg_util: {util/(i+1)}\n')

        logging.info(f'[iterations: {iterations}]\n')
        logging.info(f'Average game avg_util value: {util/iterations}')
        
        logging.info('Node_ID: [PASS, BET]')
        for _, v in sorted(node_map.items()):
            logging.info(v.toString())

    def cfr(self, cards, history, p0, p1, iter):
        '''Counterfactual regret minimization iteration'''
        plays = len(history)
        player = plays % 2
        opponent = 1 - player

        info_set = str(cards[player]) + history
        node = self._infoset_node(info_set)
        strategy = node.get_strategy(p0 if player == 0 else p1)

        payoff = self._terminal_payoff(plays, history, cards, player, opponent)

        if iter == 0 or (iter+1) % 10000 == 0:
            # logging.info(f'[iter: {iter+1}_1] hist:{history} p0:{p0} p1:{p1} '
            #              f'plays:{plays} player:{player} opp:{opponent} '
            #              f'info_set:{info_set} strategy:{strategy} payoff:{payoff}')
            logging.info(f'[iter: {iter+1}_1]\t{history}\t{p0}\t{p1}\t'
                         f'{plays}\t{player}\t{opponent}\t'
                         f'{info_set}\t{strategy}\t{payoff}')

        if payoff:
            return payoff

        # For each action, recursively call cfr with additional history and probability
        util = [0] * NUM_ACTIONS
        node_util = 0

        for a in range(NUM_ACTIONS):
            next_history = history + ('p' if a == PASS else 'b')
            
            if iter == 0 or (iter+1) % 10000 == 0:
                # logging.info(f'[iter: {iter+1}_2] next_hist:{next_history}')
                logging.info(f'[iter: {iter+1}_2]\t\t\t\t\t\t\t\t\t\t{next_history}')
            
            if player == 0:
                util[a] = - self.cfr(cards, next_history, p0 * strategy[a], p1, iter)
            else:
                util[a] = - self.cfr(cards, next_history, p0, p1 * strategy[a], iter)

            node_util += strategy[a] * util[a]
            
            if iter == 0 or (iter+1) % 10000 == 0:
                # logging.info(f'[iter: {iter+1}_3] util:{util} node_util:{node_util}')
                logging.info(f'[iter: {iter+1}_3]\t\t\t\t\t\t\t\t\t\t\t{util}\t{node_util}')

        # For each action, compute and accumulate counterfactual regret
        for a in range(NUM_ACTIONS):
            regret = util[a] - node_util
            node.regret_sum[a] += (p1 if player == 0 else p0) * regret

        if iter == 0 or (iter+1) % 10000 == 0:
            # logging.info(f'[iter: {iter+1}_4] node_util:{node_util} regret:{node.regret_sum}')
            logging.info(f'[iter: {iter+1}_4]\t\t\t\t\t\t\t\t\t\t\t\t{node_util}\t{node.regret_sum}')
        return node_util

    @staticmethod
    def _terminal_payoff(plays, history, cards, player, opponent):
        '''Return payoff for terminal states'''
        if plays > 1:
            terminal_pass = history[-1] == 'p'
            double_bet = history[-2:] == 'bb'
            player_higher = cards[player] > cards[opponent]
            if terminal_pass:
                if history == 'pp':
                    return 1 if player_higher else -1
                else:
                    return 1
            elif double_bet:
                return 2 if player_higher else -2
            return None
        else:
            return None

    @staticmethod
    def _infoset_node(info_set):
        '''Get information set node or create it if nonexistant'''
        if info_set not in node_map:
            node = Node()
            node.info_set = info_set
            node_map[info_set] = node
        node = node_map[info_set]
        return node


if __name__=="__main__":
    kp = KuhnTrainer(seed=1)
    kp.train(iterations=10000)
