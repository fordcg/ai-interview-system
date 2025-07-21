#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
支付API (来自a2)
"""

from flask import Blueprint, request, jsonify
from base.response import ResMsg

payBp = Blueprint('alipay', __name__)

@payBp.route('/pay', methods=['POST'])
def pay():
    """支付接口"""
    res = ResMsg()
    data = request.json
    
    # 模拟支付处理
    order_id = data.get('order_id')
    amount = data.get('amount')
    
    if not order_id or not amount:
        res.update(code=1, msg="订单ID和金额不能为空")
        return res.data
    
    # 这里应该有实际的支付逻辑
    # 由于是示例，我们直接返回成功
    
    res.update(code=0, data={
        'order_id': order_id,
        'amount': amount,
        'status': 'success',
        'trade_no': 'ALI' + order_id
    })
    return res.data

@payBp.route('/query', methods=['GET'])
def query():
    """查询支付状态"""
    res = ResMsg()
    order_id = request.args.get('order_id')
    
    if not order_id:
        res.update(code=1, msg="订单ID不能为空")
        return res.data
    
    # 这里应该有实际的查询逻辑
    # 由于是示例，我们直接返回成功
    
    res.update(code=0, data={
        'order_id': order_id,
        'status': 'paid',
        'trade_no': 'ALI' + order_id,
        'pay_time': '2023-07-05 12:34:56'
    })
    return res.data

@payBp.route('/refund', methods=['POST'])
def refund():
    """退款接口"""
    res = ResMsg()
    data = request.json
    
    order_id = data.get('order_id')
    amount = data.get('amount')
    
    if not order_id or not amount:
        res.update(code=1, msg="订单ID和金额不能为空")
        return res.data
    
    # 这里应该有实际的退款逻辑
    # 由于是示例，我们直接返回成功
    
    res.update(code=0, data={
        'order_id': order_id,
        'amount': amount,
        'status': 'refunded',
        'refund_no': 'REF' + order_id
    })
    return res.data 