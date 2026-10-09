"""Vercel Serverless Function 入口。

Vercel 只把 api/ 目录下的 Python 文件识别为函数入口，
真正的 Flask 应用仍在 src/main.py，这里只负责把它暴露给 Vercel。
"""
import os
import sys

# 把仓库根目录加入模块搜索路径，这样 from src.main import app 才能找到 src 包
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import app  # noqa: E402,F401
