#!/usr/bin/env python3

import os
import sys
import time
import math
import argparse
import subprocess
import re

global sample_cache
sample_cache = """
# Sample configuration for SRAM cache

-DesignTarget: cache

-CacheAccessMode: Sequential

-OptimizationTarget: ReadEDP

-EnablePruning: Yes

-ProcessNode: 22

-Capacity(KB): 256
-WordWidth(bit): 512
-Associativity(
for cache only): 16

-DeviceRoadmap: LSTP

-LocalWireType: LocalAggressive
-LocalWireRepeaterType: RepeatedNone

-LocalWireUseLowSwing: No

-GlobalWireType: GlobalAggressive
-GlobalWireRepeaterType: RepeatedNone

-GlobalWireUseLowSwing: No

-Routing: H - tree

-InternalSensing: true

-MemoryCellInputFile:./ cell_defs / SRAM.cell

-Temperature(K): 350

-BufferDesignOptimization: latency

-UseCactiAssumption: Yes
"""


""" Run
`pwd` /h/mrocke01/EECE0193/NVSim
vm-hw00{mrocke01}128: `./hw2_caches.py --cache_path /h/mrocke01/EECE0193/NVSim/cfg_files/`
"""


def cli_parse():
    parser = argparse.ArgumentParser("argument parser for cache config file iterations\nrun from this dir\n/h/mrocke01/EECE0193/NVSim/\n")
    parser.add_argument("--cache_path", action="store", help="location to generate cache files to")
    args = parser.parse_args()

    return args


def setup(args):

    global HOME
    HOME = os.getcwd()

    global cache_path
    cache_path = args.cache_path
    path_test(cache_path)


# helper functions
def shell_exec(cmd, log=False, verbose=False):
    output = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = output.communicate()
    stdout = stdout.rstrip()
    stderr = stderr.rstrip()
    output.poll()
    exit_code = output.returncode

    return stdout, stderr, exit_code


def path_test(input_path):
    if not os.path.exists(input_path):
        print(f'path not found: {input_path}\n')
        sys.exit(-1)
# helper functions


def create_cache_files():

    for cap in [16, 32, 64, 128, 256, 512, 1024, 2048]:  # 16kB to 2MB cache size

        for assoc in range(1,17):  # 1 to 16 way associative

            gen_file = f'SRAM_cache_{cap}_{assoc}.cfg'
            output_file = os.path.join(cache_path, gen_file)
            with open(output_file, 'w') as fo:

                for line in sample_cache:
                    result_cap = re.match(r"(-Capacity \(KB\): )(\d+)(\s*)", line)
                    result_assoc = re.match(r"(-Associativity (for cache only): )(\d+)(\s*)", line)

                    if result_cap:
                        capacity = result_cap.group(1) + str(cap) + result_cap.group(3)
                        fo.write(capacity)
                    elif result_assoc:
                        associativity = result_assoc.group(1) + str(assoc) + result_assoc.group(3)
                        fo.write(associativity)
                    else:
                        fo.write(line)

            fo.close()


def run_nvsim():

    nvsim_path = os.path.realpath("nvsim")
    print("\nnvsim_path", nvsim_path)
    path_test(nvsim_path)

    for root, dirs, files in os.walk(cache_path):
        print("root", root)
        for file in files: # cache file
            if re.search(r".cfg", file): # cfg files only

                output = file.split('.cfg')[0] + ".out"
                output_file = os.path.join(cache_path, output)

                full_file = os.path.join(cache_path, file)

                cmd = nvsim_path + " " + full_file + " > " + output_file
                print("\nnvsim cmd", cmd)
                shell_exec(cmd)

                print("\ncache results: ", output_file)



if __name__ == "__main__":

    args = cli_parse()

    setup(args)

    create_cache_files()

    run_nvsim()