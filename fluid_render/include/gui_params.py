from enum import Enum

class SmoothOption(Enum):
    Unsmooth = 0
    Gaussian = 1
    BilateralCombine  = 2
    BilateralSeperate = 3
    BilateralGaussian = 4
    NarrowRange       = 5

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
    MultiFrac  = 9
    Attenuation = 10
    MultiAttenuation = 11
    MultiRefract = 12

# filter_size = 21
filter_size = 10