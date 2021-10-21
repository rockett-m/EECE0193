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
size256K_levels4: - Total Area = 0.203mm^2
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



text_blob="""
./Part1_RRAM_MLC/RRAM_32K_4LV.out: - Total Area = 576.251um x 133.848um = 77130.064um^2
./Part1_RRAM_MLC/RRAM_128K_4LV.out: - Total Area = 614.203um x 133.848um = 82209.859um^2
./Part1_RRAM_MLC/RRAM_256K_4LV.out: - Total Area = 334.848um x 219.296um = 73430.934um^2
./Part1_RRAM_MLC/RRAM_512K_4LV.out: - Total Area = 344.487um x 312.752um = 107739.149um^2
./Part1_RRAM_MLC/RRAM_16K_4LV.out: - Total Area = 568.737um x 133.848um = 76124.316um^2
./Part1_RRAM_MLC/RRAM_1024K_4LV.out: - Total Area = 393.482um x 312.752um = 123062.382um^2
./Part1_RRAM_MLC/RRAM_64K_4LV.out: - Total Area = 589.489um x 133.848um = 78901.897um^2
./Part1_RRAM_MLC/RRAM_2048K_4LV.out: - Total Area = 786.965um x 312.752um = 246124.764um^2
./Part1_RRAM_SLC/RRAM_32K_2LV.out: - Total Area = 589.489um x 133.848um = 78901.897um^2
./Part1_RRAM_SLC/RRAM_128K_2LV.out: - Total Area = 334.848um x 219.296um = 73430.934um^2
./Part1_RRAM_SLC/RRAM_256K_2LV.out: - Total Area = 344.487um x 312.752um = 107739.149um^2
./Part1_RRAM_SLC/RRAM_512K_2LV.out: - Total Area = 688.975um x 312.752um = 215478.298um^2
./Part1_RRAM_SLC/RRAM_16K_2LV.out: - Total Area = 576.251um x 133.848um = 77130.064um^2
./Part1_RRAM_SLC/RRAM_64K_2LV.out: - Total Area = 614.203um x 133.848um = 82209.859um^2
./Part1_RRAM_SLC/RRAM_2048K_2LV.out: - Total Area = 819.828um x 625.504um = 512805.683um^2
./Part1_RRAM_SLC/RRAM_1024K_2LV.out: - Total Area = 786.965um x 312.752um = 246124.764um^2
./Part1_SRAM/SRAM_2048K.out: - Total Area = 1.475mm x 995.498um = 1.468mm^2
./Part1_SRAM/SRAM_256K.out: - Total Area = 954.330um x 288.958um = 275761.389um^2
./Part1_SRAM/SRAM_128K.out: - Total Area = 533.428um x 262.273um = 139903.370um^2
./Part1_SRAM/SRAM_32K.out: - Total Area = 310.274um x 131.136um = 40688.151um^2
./Part1_SRAM/SRAM_64K.out: - Total Area = 313.837um x 262.273um = 82310.718um^2
./Part1_SRAM/SRAM_1024K.out: - Total Area = 1.484mm x 526.554um = 781533.989um^2
./Part1_SRAM/SRAM_512K.out: - Total Area = 1.088mm x 497.123um = 540708.531um^2
./Part1_SRAM/SRAM_16K.out: - Total Area = 175.609um x 62.287um = 10938.201um^2"""

"""
77130.064um^2
82209.859um^2
73430.934um^2
107739.149um^2
76124.316um^2
215478.298um^2
78901.897um^2
246124.764um^2
78901.897um^2
73430.934um^2
107739.149um^2
215478.298um^2
77130.064um^2
82209.859um^2
512805.683um^2
246124.764um^2
1.468mm^2
275761.389um^2
139903.370um^2
40688.151um^2
82310.718um^2
781533.989um^2
540708.531um^2
10938.201um^2
"""

for line in text_blob.split('\n'):
    result = re.match(r"(.+):.+\s\=\s([0-9.]+)(u|m)m\^2", line)
    if result:
        # print(result.group(1), ",", result.group(2))
        print(result.group(2))



part2 = """
./Part2_RRAM_MLC_Par/RRAM_32K_4LV.out: - Total Area = 0.146mm^2
./Part2_RRAM_MLC_Par/RRAM_128K_4LV.out: - Total Area = 0.162mm^2
./Part2_RRAM_MLC_Par/RRAM_256K_4LV.out: - Total Area = 0.203mm^2
./Part2_RRAM_MLC_Par/RRAM_512K_4LV.out: - Total Area = 0.189mm^2
./Part2_RRAM_MLC_Par/RRAM_16K_4LV.out: - Total Area = 0.213mm^2
./Part2_RRAM_MLC_Par/RRAM_1024K_4LV.out: - Total Area = 0.378mm^2
./Part2_RRAM_MLC_Par/RRAM_64K_4LV.out: - Total Area = 0.148mm^2
./Part2_RRAM_MLC_Par/RRAM_2048K_4LV.out: - Total Area = 0.413mm^2
./Part2_RRAM_SLC_Par/RRAM_32K_2LV.out: - Total Area = 0.148mm^2
./Part2_RRAM_SLC_Par/RRAM_128K_2LV.out: - Total Area = 0.203mm^2
./Part2_RRAM_SLC_Par/RRAM_256K_2LV.out: - Total Area = 0.189mm^2
./Part2_RRAM_SLC_Par/RRAM_512K_2LV.out: - Total Area = 0.378mm^2
./Part2_RRAM_SLC_Par/RRAM_16K_2LV.out: - Total Area = 0.146mm^2
./Part2_RRAM_SLC_Par/RRAM_64K_2LV.out: - Total Area = 0.162mm^2
./Part2_RRAM_SLC_Par/RRAM_2048K_2LV.out: - Total Area = 0.687mm^2
./Part2_RRAM_SLC_Par/RRAM_1024K_2LV.out: - Total Area = 0.413mm^2"""

for line in part2.split('\n'):
    result = re.match(r"(.+):.+\s\=\s([0-9.]+)(u|m)m\^2", line)
    if result:
        # print(result.group(1), ",", result.group(2))
        print(result.group(1))




part2_lat = """
./Part1_SRAM/SRAM_2048K.out: -  Read Latency = 1.180ns
./Part1_SRAM/SRAM_256K.out: -  Read Latency = 316.886ps
./Part1_SRAM/SRAM_128K.out: -  Read Latency = 204.995ps
./Part1_SRAM/SRAM_32K.out: -  Read Latency = 133.093ps
./Part1_SRAM/SRAM_64K.out: -  Read Latency = 161.081ps
./Part1_SRAM/SRAM_1024K.out: -  Read Latency = 745.964ps
./Part1_SRAM/SRAM_512K.out: -  Read Latency = 413.358ps
./Part1_SRAM/SRAM_16K.out: -  Read Latency = 635.771ps
./Part1_RRAM_MLC_Ser/RRAM_32K_4LV.out: -  Read Latency = 4.790ns
./Part1_RRAM_MLC_Ser/RRAM_128K_4LV.out: -  Read Latency = 4.983ns
./Part1_RRAM_MLC_Ser/RRAM_256K_4LV.out: -  Read Latency = 4.950ns
./Part1_RRAM_MLC_Ser/RRAM_512K_4LV.out: -  Read Latency = 4.972ns
./Part1_RRAM_MLC_Ser/RRAM_16K_4LV.out: -  Read Latency = 4.744ns
./Part1_RRAM_MLC_Ser/RRAM_1024K_4LV.out: -  Read Latency = 5.225ns
./Part1_RRAM_MLC_Ser/RRAM_64K_4LV.out: -  Read Latency = 4.852ns
./Part1_RRAM_MLC_Ser/RRAM_2048K_4LV.out: -  Read Latency = 5.278ns
./Part1_RRAM_SLC_Ser/RRAM_32K_2LV.out: -  Read Latency = 1.939ns
./Part1_RRAM_SLC_Ser/RRAM_128K_2LV.out: -  Read Latency = 2.042ns
./Part1_RRAM_SLC_Ser/RRAM_256K_2LV.out: -  Read Latency = 2.064ns
./Part1_RRAM_SLC_Ser/RRAM_512K_2LV.out: -  Read Latency = 2.104ns
./Part1_RRAM_SLC_Ser/RRAM_16K_2LV.out: -  Read Latency = 1.877ns
./Part1_RRAM_SLC_Ser/RRAM_64K_2LV.out: -  Read Latency = 2.070ns
./Part1_RRAM_SLC_Ser/RRAM_2048K_2LV.out: -  Read Latency = 2.288ns
./Part1_RRAM_SLC_Ser/RRAM_1024K_2LV.out: -  Read Latency = 2.370ns
./Part2_RRAM_MLC_Par/RRAM_32K_4LV.out: -  Read Latency = 1.877ns
./Part2_RRAM_MLC_Par/RRAM_32K_4LV.out: -  Read Latency = 1.842ns
./Part2_RRAM_MLC_Par/RRAM_128K_4LV.out: -  Read Latency = 2.070ns
./Part2_RRAM_MLC_Par/RRAM_128K_4LV.out: -  Read Latency = 1.884ns
./Part2_RRAM_MLC_Par/RRAM_256K_4LV.out: -  Read Latency = 2.042ns
./Part2_RRAM_MLC_Par/RRAM_256K_4LV.out: -  Read Latency = 1.902ns
./Part2_RRAM_MLC_Par/RRAM_512K_4LV.out: -  Read Latency = 2.064ns
./Part2_RRAM_MLC_Par/RRAM_512K_4LV.out: -  Read Latency = 1.888ns
./Part2_RRAM_MLC_Par/RRAM_16K_4LV.out: -  Read Latency = 1.830ns
./Part2_RRAM_MLC_Par/RRAM_16K_4LV.out: -  Read Latency = 1.710ns
./Part2_RRAM_MLC_Par/RRAM_1024K_4LV.out: -  Read Latency = 2.104ns
./Part2_RRAM_MLC_Par/RRAM_1024K_4LV.out: -  Read Latency = 1.917ns
./Part2_RRAM_MLC_Par/RRAM_64K_4LV.out: -  Read Latency = 1.939ns
./Part2_RRAM_MLC_Par/RRAM_64K_4LV.out: -  Read Latency = 1.846ns
./Part2_RRAM_MLC_Par/RRAM_2048K_4LV.out: -  Read Latency = 2.370ns
./Part2_RRAM_MLC_Par/RRAM_2048K_4LV.out: -  Read Latency = 2.006ns
./Part2_RRAM_SLC_Par/RRAM_32K_2LV.out: -  Read Latency = 1.939ns
./Part2_RRAM_SLC_Par/RRAM_32K_2LV.out: -  Read Latency = 1.846ns
./Part2_RRAM_SLC_Par/RRAM_128K_2LV.out: -  Read Latency = 2.042ns
./Part2_RRAM_SLC_Par/RRAM_128K_2LV.out: -  Read Latency = 1.902ns
./Part2_RRAM_SLC_Par/RRAM_256K_2LV.out: -  Read Latency = 2.064ns
./Part2_RRAM_SLC_Par/RRAM_256K_2LV.out: -  Read Latency = 1.888ns
./Part2_RRAM_SLC_Par/RRAM_512K_2LV.out: -  Read Latency = 2.104ns
./Part2_RRAM_SLC_Par/RRAM_512K_2LV.out: -  Read Latency = 1.917ns
./Part2_RRAM_SLC_Par/RRAM_16K_2LV.out: -  Read Latency = 1.877ns
./Part2_RRAM_SLC_Par/RRAM_16K_2LV.out: -  Read Latency = 1.842ns
./Part2_RRAM_SLC_Par/RRAM_64K_2LV.out: -  Read Latency = 2.070ns
./Part2_RRAM_SLC_Par/RRAM_64K_2LV.out: -  Read Latency = 1.884ns
./Part2_RRAM_SLC_Par/RRAM_2048K_2LV.out: -  Read Latency = 2.288ns
./Part2_RRAM_SLC_Par/RRAM_2048K_2LV.out: -  Read Latency = 2.088ns
./Part2_RRAM_SLC_Par/RRAM_1024K_2LV.out: -  Read Latency = 2.370ns
./Part2_RRAM_SLC_Par/RRAM_1024K_2LV.out: -  Read Latency = 2.006ns"""



for line in part2_lat.split('\n'):
    result = re.match(r"(.+):.+\s\=\s([0-9.]+)(p|n)s", line)
    if result:
        print(result.group(1), result.group(2))
        # print(result.group(1))
