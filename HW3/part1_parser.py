#!/usr/bin/env python3

import os, sys, re

text = """size1024K_levels16: - Total Area = 0.297mm^2
size1024K_levels4: - Total Area = 0.378mm^2
size128K_levels16: - Total Area = 0.148mm^2
size128K_levels4: - Total Area = 0.162mm^2
size16K_levels16: - Total Area = 0.145mm^2
size16K_levels4: - Total Area = 0.213mm^2
size2048K_levels16: - Total Area = 0.378mm^2
size2048K_levels4: - Total Area = 0.413mm^2
size256K_levels16: - Total Area = 0.162mm^2
size256K_levels4: - Total Area = 0.345mm^2
size32K_levels16: - Total Area = 0.213mm^2
size32K_levels4: - Total Area = 0.148mm^2
size4096K_levels16: - Total Area = 0.413mm^2
size4096K_levels4: - Total Area = 0.687mm^2
size512K_levels16: - Total Area = 0.203mm^2
size512K_levels4: - Total Area = 0.189mm^2
size64K_levels16: - Total Area = 0.146mm^2
size64K_levels4: - Total Area = 0.148mm^2"""

for line in text.split('\n'):
    result = re.match(r"(.+):.+(0.[0-9]+)mm\^2", line)
    if result:
        print(result.group(1), ",", result.group(2))