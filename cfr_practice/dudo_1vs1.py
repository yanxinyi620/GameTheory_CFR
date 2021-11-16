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

