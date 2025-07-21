#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基于物品的协同过滤 (来自a2)
"""

import math
import random
from operator import itemgetter

class ItemBasedCF:
    """基于物品的协同过滤推荐算法"""
    
    def __init__(self):
        # 训练集
        self.train_set = {}
        # 测试集
        self.test_set = {}
        # 物品相似度矩阵
        self.item_sim_matrix = {}
        # 物品流行度
        self.item_popular = {}
        # 用户
        self.users = set()
        # 物品
        self.items = set()
        
        # 初始化数据
        self.load_data()
        self.calc_item_sim()
    
    def load_data(self):
        """加载数据"""
        # 模拟数据，实际应从数据库加载
        # 用户-物品评分矩阵
        ratings = [
            [1, 101, 5.0],
            [1, 102, 4.0],
            [1, 103, 3.0],
            [2, 101, 4.0],
            [2, 104, 5.0],
            [3, 102, 5.0],
            [3, 103, 4.0],
            [3, 104, 3.0],
            [4, 101, 4.0],
            [4, 103, 5.0],
            [4, 104, 4.0]
        ]
        
        # 划分训练集和测试集
        for user, item, rating in ratings:
            self.users.add(user)
            self.items.add(item)
            
            # 90%作为训练集
            if random.random() < 0.9:
                self.train_set.setdefault(user, {})
                self.train_set[user][item] = rating
            else:
                self.test_set.setdefault(user, {})
                self.test_set[user][item] = rating
    
    def calc_item_sim(self):
        """计算物品相似度矩阵"""
        # 统计物品流行度
        for user, items in self.train_set.items():
            for item in items:
                self.item_popular.setdefault(item, 0)
                self.item_popular[item] += 1
        
        # 构建物品-用户倒排表
        item_users = {}
        for user, items in self.train_set.items():
            for item in items:
                item_users.setdefault(item, set())
                item_users[item].add(user)
        
        # 计算物品相似度矩阵
        for i, users_i in item_users.items():
            for j, users_j in item_users.items():
                if i == j:
                    continue
                self.item_sim_matrix.setdefault(i, {})
                # 物品i和j共同被多少用户喜欢
                self.item_sim_matrix[i][j] = len(users_i & users_j)
                # 使用余弦相似度计算物品相似度
                self.item_sim_matrix[i][j] /= math.sqrt(len(users_i) * len(users_j))
    
    def recommend(self, user, k=5, n=10):
        """推荐算法
        
        Args:
            user: 用户ID
            k: 取相似度最高的k个物品
            n: 推荐n个物品
        
        Returns:
            推荐列表 [(物品ID, 推荐评分), ...]
        """
        # 如果用户不在训练集中，返回热门物品
        if user not in self.train_set:
            sorted_items = sorted(self.item_popular.items(), key=itemgetter(1), reverse=True)
            return [{'job_id': item[0], 'score': item[1]} for item in sorted_items[:n]]
        
        # 用户已评分物品
        user_items = self.train_set[user]
        
        # 用户未评分物品的预测评分
        rank = {}
        for item_i, rating_i in user_items.items():
            for item_j, sim in sorted(self.item_sim_matrix.get(item_i, {}).items(), key=itemgetter(1), reverse=True)[:k]:
                if item_j in user_items:
                    continue
                rank.setdefault(item_j, 0)
                rank[item_j] += sim * rating_i
        
        # 返回推荐列表
        sorted_rank = sorted(rank.items(), key=itemgetter(1), reverse=True)
        return [{'job_id': item[0], 'score': item[1]} for item in sorted_rank[:n]] 