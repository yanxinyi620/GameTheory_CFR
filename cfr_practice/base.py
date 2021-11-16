#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :  base.py
@Time    :  2021/11/13 00:03:36
@Author  :  yanxinyi
@Version :  v1.0
@Contact :  yanxinyi620@163.com
@Desc    :  A base model for Counterfactual Regret Minimization algorithm.
'''

class BaseCFR(object):
    
    def __init__(self):
        self._my_strategies = None

    @property
    def my_strategies(self):
        return self._my_strategies

    @my_strategies.setter
    def my_strategies(self, value):
        self._my_strategies = value

    def train(self, iterations, *args, **kwargs):
        raise NotImplementedError
