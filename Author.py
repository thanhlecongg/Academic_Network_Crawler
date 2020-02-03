# Created by Thanh C. Le at 2020-01-31
import pprint

import numpy as np
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
from tqdm import tqdm
class Author(object):
    def __init__(self,name,homepage):
        self.name = name
        self.homepage = homepage
    def __str__(self):
        return pprint.pformat(self.__dict__)