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
    # parser.add_argument("--of", "--output_folder", action="store", dest="output_folder", help="output generated files")
    parser.add_argument("--debug", action="store_true", help="debug mode (prints paths etc.)")
    args = parser.parse_args()
    return args


def setup_env(args):
    treeroot = args.treeroot
    input_folder = args.input_folder
    # output_folder = args.output_folder
    debug = args.debug

    # for x in [ treeroot, input_folder, output_folder ]:
    for x in [ treeroot, input_folder ]:
        path_test(x)

    print(f'\nHOME: {HOME}')
    print(f'\ntreeroot: {treeroot}')
    print(f'\ninput_folder: {input_folder}')
    # print(f'\noutput_folder: {output_folder}\n')

    # return treeroot, input_folder, output_folder
    return treeroot, input_folder, debug


def build_cfg_data(opt_target, capacity, cell):
    cfg_data = (f'\n'
                f'-DesignTarget: RAM\n'
                f'-OptimizationTarget: {opt_target}\n'
                f'-EnablePruning: Yes\n'
                f'\n'
                f'-ProcessNode: 22\n'
                f'-Capacity (KB): {capacity}\n'
                f'-WordWidth (bit): 128\n'
                f'\n'
                f'-DeviceRoadmap: LSTP\n'
                f'-LocalWireType: LocalAggressive\n'
                f'-LocalWireRepeaterType: RepeatedNone\n'
                f'\n'
                f'-LocalWireUseLowSwing: No\n'
                f'-GlobalWireType: GlobalAggressive\n'
                f'-GlobalWireRepeaterType: RepeatedNone\n'
                f'-GlobalWireUseLowSwing: No\n'
                f'\n'
                f'-Routing: H-tree\n'
                f'-InternalSensing: true\n'
                f'-MemoryCellInputFile: ./cell_defs/{cell}.cell\n'
                f'\n'
                f'-Temperature (K): 350\n'
                f'-BufferDesignOptimization: latency\n'
                f'-UseCactiAssumption: Yes\n\n')

    return cfg_data


def create_cfg_files(treeroot, input_folder, debug):

    for iso in [ "iso_area", "iso_capacity" ]:
        iso_path = os.path.join(input_folder, iso)

        for opt_target in [ "ReadLatency", "WriteLatency", "ReadDynamicEnergy", "WriteDynamicEnergy", "ReadEDP", "WriteEDP", "LeakagePower", "Area" ]:
            opt_path = os.path.join(iso_path, opt_target)

            for cell in [ "STTRAM", "SRAM", "RRAM", "PCRAM" ]:
                cell_path = os.path.join(opt_path, cell)

                for capacity in [ "16", "32", "64", "128", "256", "512", "1024", "2048", "4096" ]:
                    cfg_name = capacity + "KB"
                    cap_path = os.path.join(cell_path, cfg_name)

                    if not os.path.exists(cap_path): os.makedirs(cap_path, exist_ok=True)
                    path_test(cap_path)

                    cfg_filename = capacity + "KB.cfg"
                    cfg_file = os.path.join(cap_path, cfg_filename)
                    if not os.path.exists(cfg_file):
                        cmd_create = "touch " + cfg_file; os.system(cmd_create)
                        cmd_chmod = "chmod 750 " + cfg_file; os.system(cmd_chmod)
                        path_test(cfg_file)

                    cfg_data = build_cfg_data(opt_target, capacity, cell)

                    with open(cfg_file, 'w') as fc:
                        print(cfg_file)
                        fc.write(cfg_data)
                    fc.close()

                    if debug:
                        print(f'\ntreeroot: {treeroot}\n'
                              f'\ninput_folder: {input_folder}\n'
                              f'\niso_path: {iso_path}\n'
                              f'\nopt_path: {opt_path}\n'
                              f'\ncap_path: {cap_path}\n'
                              f'\ncell_path: {cell_path}\n'
                              f'\ncfg_file: {cfg_file}\n')
                        sys.exit()


if __name__ == "__main__":

    t0 = time.perf_counter()

    args = cli_parse()

    # treeroot, input_folder, output_folder = setup_env(args)
    treeroot, input_folder, debug = setup_env(args)

    # main(treeroot, input_folder, output_folder)
    create_cfg_files(treeroot, input_folder, debug) # calls build_cfg_data()

    # unique folder and cfg file and output file in specific test case dir
    # plotting like matplotlib
    # before monday run 3D tests as well to see if destiny works...

    t1 = time.perf_counter()

    pretty_time(t0, t1)

    sys.exit()

""" parameters that change for each dir / test
-OptimizationTarget: [ ReadLatency, WriteLatency, ReadDynamicEnergy, WriteDynamicEnergy, ReadEDP, WriteEDP, LeakagePower, Area]
-Capacity (KB): [ 16, 32, 64, 128, 256, 512, 1024, 2048, 4096 ]
-MemoryCellInputFile: ./cell_defs/SRAM.cell
"""

# Sample configuration for SRAM cache
cfg_info_archive = """
-DesignTarget: RAM
-OptimizationTarget: {}
-EnablePruning: Yes

-ProcessNode: 22
-Capacity (KB): {}
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

# cmd = "find . -name '*'"
# filelist = shell_exec(cmd)
# dir_list = []
# # print(filelist)
#
# for line in filelist:
#     if type(line) == str and re.search(r"./.+", line):
#         print(line[3:])
#         newline = os.path.join(root, line[1:])
#         path_test(newline)
#         print(newline)
#         dir_list.append(str(newline))
# print(struct)