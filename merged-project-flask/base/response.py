#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
响应处理
"""

from flask import jsonify

class ResMsg(object):
    """
    封装响应文本
    """
    def __init__(self, data=None, code=0, msg=""):
        self._data = data
        self._code = code
        self._msg = msg

    def update(self, code=None, data=None, msg=None):
        """
        更新响应数据
        """
        if code is not None:
            self._code = code
        if data is not None:
            self._data = data
        if msg is not None:
            self._msg = msg

    @property
    def data(self):
        """
        获取响应数据
        """
        return jsonify({
            "code": self._code,
            "msg": self._msg,
            "data": self._data
        }) 