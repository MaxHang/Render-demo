from enum import Enum

class SmoothOption(Enum):
    Unsmooth = 0
    Guassian = 1
    BilateralCombine  = 2
    BilateralSeperate = 3

class ShaderOption(Enum):
    Full    = 0
    Depth   = 1
    Thick   = 2
    Normal  = 3
    Fresnel = 4
    Reflect = 5
    Refract = 6
    BlinnPhong = 7
    MultiFluid = 8
    MultiFluid2 = 9
    Attenuation = 10

# filter_size = 21
filter_size = 10