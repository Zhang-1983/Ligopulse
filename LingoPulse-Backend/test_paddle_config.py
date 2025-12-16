#!/usr/bin/env python3
# 测试飞桨平台配置加载

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import get_settings, get_llm_settings

print("=== 测试飞桨平台配置加载 ===")

# 获取设置对象
settings = get_settings()
llm_settings = get_llm_settings()

# 打印飞桨相关配置
print("飞桨平台基本配置：")
print(f"- paddle_access_token: {'已配置' if settings.paddle_access_token else '未配置'}")
print(f"- paddle_base_url: {settings.paddle_base_url}")
print(f"- paddle_model_name: {settings.paddle_model_name}")

print("\nLLM提供商飞桨配置：")
print(f"- paddle_temperature: {llm_settings.paddle_temperature}")
print(f"- paddle_max_tokens: {llm_settings.paddle_max_tokens}")

print("\n百度AI Studio配置：")
print(f"- baidu_access_token: {'已配置' if llm_settings.baidu_access_token else '未配置'}")
print(f"- baidu_base_url: {llm_settings.baidu_base_url}")
print(f"- baidu_model: {llm_settings.baidu_model}")

print("\n=== 配置测试完成 ===")
