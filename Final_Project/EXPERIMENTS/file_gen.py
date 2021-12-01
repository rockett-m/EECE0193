#!/usr/bin/env python3

import os
import sys
import time
import math
import argparse
import subprocess
import re
import csv

global HOME
HOME = os.getcwd()


# helper functions
def shell_exec(cmd, log=False, verbose=False):
    output = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = output.communicate()[0].decode('utf-8').strip(), output.communicate()[1]
    exit_code = output.returncode

    if log:
        lf = open(log, 'a+')
        lf.write(f'\nshell cmd:\t{cmd}\n\n')
        if (len(stdout) > 0) and verbose:
            # record(msg, results_log)
            lf.write(f'\n{stdout}\n')
        lf.close()

    return stdout, stderr, exit_code


def path_test(input_path):
    if not os.path.exists(input_path):
        print(f'path not found: {input_path}\n')
        sys.exit(-1)


def pretty_time(t0: float, t1: float):
    # t0 = time.perf_counter()  # call in script
    # t1 = time.perf_counter()  # call in script
    time_delta: float = t1 - t0
    if time_delta < 60:
        msg = f'\nelapsed time: {round(time_delta, 3)} seconds\n'
    else:
        mins = int(math.floor(time_delta / 60))
        secs = int(math.floor(time_delta % 60))
        msg = f'\nelapsed time: {mins} min {secs} secs\n'

    print(msg)
    return msg
# helper functions


def cli_parse():
    parser = argparse.ArgumentParser(description="cli parser")
    parser.add_argument("--treeroot", action="store", dest="treeroot", help="root folder of all code")
    parser.add_argument("--if", "--input_folder", action="store", dest="input_folder", help="input cfg files")
    parser.add_argument("--of", "--output_folder", action="store", dest="output_folder", help="output generated files")
    args = parser.parse_args()
    return args


def setup_env(args):
    treeroot = args.treeroot
    input_folder = args.input_folder
    output_folder = args.input_folder

    for x in [ treeroot, input_folder, output_folder ]:
        path_test(x)

    print(f'\nHOME: {HOME}')
    print(f'\ntreeroot: {treeroot}')
    print(f'\ninput_folder: {input_folder}')
    print(f'\noutput_folder: {output_folder}\n')

    return treeroot, input_folder, output_folder


def main(treeroot, input_folder, output_folder):

    # for root, dirs, files in os.walk(treeroot):
    #     for d in dirs:
    #         print(d)


    # input files
    input_files = []
    basepath = os.path.join(treeroot, "Input/NVSim/")
    # print(basepath)

    for iso in [ "iso_area", "iso_capacity" ]:
        iso_path = os.path.join(basepath, iso)
        # print(iso_path)

        # for param in [ "RL", "WL", "RE", "WE", "LP", "AR" ]:
        #     param_path = os.path.join(iso_path, param)
        #     # print(param_path)

        for opt_target in [ "ReadLatency", "WriteLatency", "ReadDynamicEnergy", "WriteDynamicEnergy", "ReadEDP", "WriteEDP", "LeakagePower", "Area" ]:
            opt_path = os.path.join(iso_path, opt_target)

            for cell in [ "STTRAM", "SRAM", "RRAM", "PCRAM" ]:
                cell_path = os.path.join(opt_path, cell)
                if not os.path.exists(cell_path): os.mkdir(cell_path)
                path_test(cell_path)
                print(cell_path)

                input_files.append(cell_path)

    # output files

    print("")
    sys.exit()

    cmd = "find . -name '*'"
    filelist = shell_exec(cmd)
    dir_list = []
    # print(filelist)

    for line in filelist:
        if type(line) == str and re.search(r"./.+", line):
            print(line[3:])
            newline = os.path.join(root, line[1:])
            path_test(newline)
            print(newline)
            dir_list.append(str(newline))
    # print(struct)


""" parameters that change for each dir / test
-DesignTarget: RAM
-OptimizationTarget: [ ReadLatency, WriteLatency, ReadDynamicEnergy, WriteDynamicEnergy, ReadEDP, WriteEDP, LeakagePower, Area]
-Capacity (KB): 256
-MemoryCellInputFile: ./cell_defs/SRAM.cell
"""

# Sample configuration for SRAM cache
cfg_info = """
-DesignTarget: RAM
-OptimizationTarget: ReadEDP
-EnablePruning: Yes

-ProcessNode: 22
-Capacity (KB): [ 16, 32, 64, 128, 256, 512, 1024, 2048, 4096 ]
-WordWidth (bit): 128

-DeviceRoadmap: LSTP
-LocalWireType: LocalAggressive
-LocalWireRepeaterType: RepeatedNone

-LocalWireUseLowSwing: No
-GlobalWireType: GlobalAggressive
-GlobalWireRepeaterType: RepeatedNone
-GlobalWireUseLowSwing: No

-Routing: H-tree
-InternalSensing: true
-MemoryCellInputFile: ./cell_defs/SRAM.cell

-Temperature (K): 350
-BufferDesignOptimization: latency
-UseCactiAssumption: Yes"""


if __name__ == "__main__":

    t0 = time.perf_counter()

    args = cli_parse()

    treeroot, input_folder, output_folder = setup_env(args)

    main(treeroot, input_folder, output_folder)

    # unique folder and cfg file and output file in specific test case dir
    # plotting like matplotlib
    # before monday run 3D tests as well to see if destiny works...


    # create_cache_files()

    # run_nvsim_part1()

    # struct_part1 = send_to_csv_part1()

    # write_csv_part1(struct_part1)

    # memory_cell_edits()

    # run_nvsim_part2()

    # struct_part2 = send_to_csv_part2()

    # write_csv_part2(struct_part2)

    # create_ram_files()

    # run_nvsim_part3()

    # struct_part3 = send_to_csv_part3()

    # write_csv_part3(struct_part3)

    t1 = time.perf_counter()

    pretty_time(t0, t1)
