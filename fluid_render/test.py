import numpy as np

sigma = 2  # 定义标准差
n = 15  # 定义数组长度

# 生成一维高斯分布数组
x = np.linspace(-(n//2), n//2, n)
weights = np.exp(-(x**2)/(2*sigma**2)) / (sigma * np.sqrt(2*np.pi))

# 对数组进行规范化
weights /= np.sum(weights)

for i in range(n):
    print(f'{weights[i]}', end=', ')

