



def cal_fresnel_R0(n1:float, n2:float):
    """计算菲涅尔效果, 使用 Schlick近似计算R0
    """
    R0 = ((n1 - n2) / (n1 + n2)) ** 2
    return R0

# n1 = 1.33
# n2 = 1.0
# R0 = cal_fresnel_R0(n1, n2)
# Fs = R0 + (1 - R0)(1 - )