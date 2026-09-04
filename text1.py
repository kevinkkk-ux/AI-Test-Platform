# 测试是否安装numpy示例
try:
    import numpy
    print("✅numpy已安装，版本：", numpy.__version__)
except ModuleNotFoundError:
    print("❌numpy没有安装")
