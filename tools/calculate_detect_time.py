#!/usr/bin/env python3
"""
Created on 

@author: yangshifu
@mail: yangshifu@sensetime.com
"""
import re
import numpy as np
import pandas as pd
from pathlib import Path

log_path = r'D:\doc\test_detect_rate\ppl\log'


elapse = []

for log_ in Path(log_path).glob('*ir*.log'):
    print(log_.name)
    content = log_.read_text()
    a = re.findall(r'\[\s*(\d{1,4}\.\d{4})\s*ms\]\sCHECK_BREAK', content)
    anp = np.array(a[1:], dtype=np.float32)
    avg = np.mean(anp)
    min = np.min(anp)
    max = np.max(anp)
    # std = np.std(anp)
    print('avg: {:.4f}'.format(avg))
    print('min: {:.4f}'.format(min))
    print('max: {:.4f}'.format(max))
    # print('std: {:.4f}'.format(std))
    elapse.append(anp)
