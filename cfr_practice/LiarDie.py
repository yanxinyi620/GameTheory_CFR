#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :  LiarDie.py
@Time    :  2021/11/15 00:08:33
@Author  :  yanxinyi
@Version :  v1.0
@Contact :  yanxinyi620@163.com
@Desc    :  Applying algorithm of Fixed-Strategy Iteration Counterfactual Regret Minimization 
            (FSICFR) to Liar Die.

java code structure:
    class Node {
        <Liar Die node definitions>
        <Liar Die node constructor>
        <Get Liar Die node current mixed strategy through regret-matching>
        <Get Liar Die node average mixed strategy>
    }

    public void train(int iterations) {
        double[] regret = new double[sides];
        int[] rollAfterAcceptingClaim = new int[sides];
        for (int iter = 0; iter < iterations; iter++) {
            <Initialize rolls and starting probabilities>
            <Accumulate realization weights forward>
            <Backpropagate utilities, adjusting regrets and strategies>
            <Reset strategy sums after half of training>
        }
        <Print resulting strategy>
    }

    public class LiarDieTrainer {
        <Liar Die definitions>
        <Liar Die player decision node>
        <Construct trainer and allocate player decision nodes>
        <Train with FSICFR>
        <LiarDieTrainer main method>
    }
'''

import random


class Node(object):
    '''Liar Die player decision node'''

    def __init__(self, numActions, *args, **kwargs):
        '''Liar Die node definitions'''
        self.regretSum = [0] * numActions
        self.strategy = [0] * numActions
        self.strategySum = [0] * numActions
        self.u = 0
        self.pPlayer = 0
        self.pOpponent = 0

    def getStrategy(self):
        '''Get Liar Die node current mixed strategy through regret-matching'''
        normalizingSum = 0
        for i in range(len(self.strategy)):
            self.strategy[i] = max(self.regretSum[i], 0)
            normalizingSum += self.strategy[i]

        for i in range(len(self.strategy)):
            if normalizingSum > 0:
                self.strategy[i] /= normalizingSum
            else:
                self.strategy[i] = 1/len(self.strategy)

        for i in range(len(self.strategy)):
            self.strategySum[i] += self.pPlayer * self.strategy[i]

        return self.strategy

    def getAverageStrategy(self):
        '''Get Liar Die node average mixed strategy'''
        normalizingSum = 0
        for i in range(len(self.strategySum)):
            normalizingSum += self.strategySum[i]

        for i in range(len(self.strategySum)):
            if normalizingSum > 0:
                self.strategySum[i] /= normalizingSum
            else:
                self.strategySum[i] = 1 / len(self.strategySum)

        return self.strategySum


class LDTrainer(object):

    def __init__(self, seed=None, sides=6, *args, **kwargs):
        
        random.seed(seed)

        '''Liar Die definitions'''
        self.DOUBT = 0
        self.ACCEPT = 1

        # Construct trainer and allocate player decision nodes
        self.sides = sides
        self.responseNodes = [[0]*(self.sides + 1) for _ in range(self.sides)]
        self.claimNodes = [[0]*(self.sides + 1) for _ in range(self.sides)]

        for myClaim in range(self.sides + 1):
            for oppClaim in range(myClaim + 1, self.sides + 1):
                self.responseNodes[myClaim][oppClaim] = \
                    Node(1 if (oppClaim == 0 or oppClaim == self.sides) else 2)
        
        for oppClaim in range(self.sides):
            for roll in range(1, self.sides + 1):
                self.claimNodes[oppClaim][roll] = Node(self.sides - oppClaim)

    def train(self, iterations):
        '''Train with FSICFR'''
        regret = [0] * self.sides
        rollAfterAcceptingClaim = [0] * self.sides
        for iter in range(iterations):

            # Initialize rolls and starting probabilities
            for i in range(len(rollAfterAcceptingClaim)):
                rollAfterAcceptingClaim[i] = random.randint(0, self.sides - 1) + 1
            self.claimNodes[0][rollAfterAcceptingClaim[0]].pPlayer = 1
            self.claimNodes[0][rollAfterAcceptingClaim[0]].pOpponent = 1

            # Accumulate realization weights forward
            for oppClaim in range(0, self.sides + 1):
                # Visit response Nodes forward
                if oppClaim > 0:
                    for myClaim in range(0, oppClaim):
                        node = self.responseNodes[myClaim][oppClaim]
                        actionProb = node.getStrategy()
                        if oppClaim < self.sides:
                            nextNode = self.claimNodes[oppClaim][rollAfterAcceptingClaim[oppClaim]]
                            nextNode.pPlayer += actionProb[1] * node.pPlayer
                            nextNode.pOpponent += node.pOpponent

                # Visit claim nodes forward
                if oppClaim < self.sides:
                    node = self.claimNodes[oppClaim][rollAfterAcceptingClaim[oppClaim]]
                    actionProb = node.getStrategy()
                    for myClaim in range(oppClaim + 1, self.sides + 1):
                        nextClaimProb = actionProb[myClaim - oppClaim - 1]
                        if nextClaimProb > 0:
                            nextNode = self.responseNodes[oppClaim][myClaim]
                            nextNode.pPlayer += node.pOpponent
                            nextNode.pOpponent += nextClaimProb * node.pPlayer

            # Backpropagate utilities, adjusting regrets and strategies
            for oppClaim in range(self.sides, -1, -1):
                # Visit claim nodes backward
                if oppClaim < self.sides:
                    node = self.claimNodes[oppClaim][rollAfterAcceptingClaim[oppClaim]]
                    actionProb = node.strategy
                    node.u = 0
                    for myClaim in range(oppClaim + 1, self.sides + 1):
                        actionIndex = myClaim - oppClaim - 1
                        nextNode = self.responseNodes[oppClaim][myClaim]
                        childUtil = - nextNode.u
                        regret[actionIndex] = childUtil
                        node.u += actionProb[actionIndex] * childUtil
                    for a in range(len(actionProb)):
                        regret[a] -= node.u
                        node.regretSum[a] += node.pOpponent * regret[a]
                    node.pPlayer = node.pOpponent = 0
                    
                # Visit response nodes backward
                if oppClaim > 0:
                    for myClaim in range(0, oppClaim):
                        node = self.responseNodes[myClaim][oppClaim]
                        actionProb = node.strategy
                        node.u = 0
                        doubtUtil = 1 if (oppClaim > rollAfterAcceptingClaim[myClaim]) else -1
                        regret[self.DOUBT] = doubtUtil
                        if oppClaim < self.sides:
                            nextNode = self.claimNodes[oppClaim][rollAfterAcceptingClaim[oppClaim]]
                            regret[self.ACCEPT] = nextNode.u
                            node.u += actionProb[self.ACCEPT] * nextNode.u
                        for a in range(len(actionProb)):
                            regret[a] -= node.u
                            node.regretSum[a] += node.pOpponent * regret[a]
                        node.pPlayer = node.pOpponent = 0

            # Reset strategy sums after half of training
            if iter == iterations / 2:
                for nodes in self.responseNodes:
                    for node in nodes:
                        if node:
                            for a in range(len(node.strategySum)):
                                node.strategySum[a] = 0

                for nodes in self.claimNodes:
                    for node in nodes:
                        if node:
                            for a in range(len(node.strategySum)):
                                node.strategySum[a] = 0

        # Print resulting strategy
        for initialRoll in range(1, self.sides + 1):
            print("Initial claim policy with roll {0:d}: ".format(initialRoll), end = '')
            for prob in self.claimNodes[0][initialRoll].getAverageStrategy():
                print('{0:.2f} '.format(prob), end = '')
            print('')
        
        print('\nOld_Claim\tNew_Claim\tAction_Probabilities')
        for myClaim in range(0, self.sides + 1):
            for oppClaim in range(myClaim + 1, self.sides + 1):
                print('{0:d}\t{1:d}\t'.format(myClaim, oppClaim) + \
                      str([float('%.4g' % float('%.3f' % x)) for x in \
                           self.responseNodes[myClaim][oppClaim].getAverageStrategy()]))

        print('\nOld_Claim\tRoll\tAction_Probabilities')
        for oppClaim in range(0, self.sides):
            for roll in range(1, self.sides + 1):
                print('{0:d}\t{1:d}\t'.format(oppClaim, roll) + \
                      str([float('%.3g' % float('%.2f' % x)) for x in \
                           self.claimNodes[oppClaim][roll].getAverageStrategy()]))
                # print('regrets', self.claimNodes[oppClaim][roll].regretSum)


if __name__ == "__main__":
    LD = LDTrainer(seed=1, sides=6)
    LD.train(iterations = 10000)
