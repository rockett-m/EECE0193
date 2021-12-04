#!/usr/bin/env python3

# sample of how to run
# python3 file_gen.py --tree_root /Users/sudo/CodeProjects/Tufts/EECE0193/Final_Project/EXPERIMENTS
# --if /Users/sudo/CodeProjects/Tufts/EECE0193/Final_Project/EXPERIMENTS/Input/NVSim/

# python3 file_gen.py --tree_root /Users/sudo/CodeProjects/Tufts/EECE0193/Final_Project/EXPERIMENTS
# --if /Users/sudo/CodeProjects/Tufts/EECE0193/Final_Project/EXPERIMENTS/Input/Destiny/

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
    parser.add_argument("--tree_root", action="store", dest="tree_root", help="root folder of all code")
    parser.add_argument("--if", "--input_folder", action="store", dest="input_folder", help="input cfg files")
    parser.add_argument("--tool_path", action="store", dest="tool_path", help="root dir of nvsim or destiny with executable")
    parser.add_argument("--debug", action="store_true", help="debug mode (prints paths etc.)")
    args = parser.parse_args()
    return args


def setup_env(args):
    tree_root = args.tree_root
    input_folder = args.input_folder
    tool_path = args.tool_path
    debug = args.debug

    for x in [ tree_root, input_folder, tool_path ]:
        path_test(x)

    print(f'\nHOME: {HOME}')
    print(f'\ntree_root: {tree_root}')
    print(f'\ninput_folder: {input_folder}')
    print(f'\ntool_path: {tool_path}\n')

    return tree_root, input_folder, tool_path, debug


def build_cfg_data(software, opt_target, capacity, cell):
    cfg_data = ""
    if software == "NVSim":
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

    elif software == "Destiny":
        cfg_data = (f'\n'
                    f'-DesignTarget: RAM\n'
                    f'-OptimizationTarget: {opt_target}\n'
                    f'-EnablePruning: Yes\n'
                    f'\n'
                    f'-ProcessNode: 22\n'
                    f'-Capacity(KB): {capacity}\n'
                    f'-WordWidth(bit): 128\n'
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
                    f'-MemoryCellInputFile: config/sample_{cell}.cell\n'
                    f'\n'
                    f'-Temperature(K): 350\n'
                    f'-BufferDesignOptimization: latency\n'
                    f'-StackedDieCount: 1\n\n')

    else:
        print("need to enter NVSim or Destiny for cfg file generation")
        sys.exit()
    return cfg_data


def create_cfg_files(tree_root, input_folder, debug):

    filelist = []

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

                    cfg_data = ""
                    if re.search(r"NVSim", input_folder, re.I):
                        cfg_data = build_cfg_data("NVSim", opt_target, capacity, cell)
                    elif re.search(r"Destiny", input_folder, re.I):
                        cfg_data = build_cfg_data("Destiny", opt_target, capacity, cell)
                    else:
                        print("expecting NVsim or Destiny in the input folder path")
                        sys.exit()

                    with open(cfg_file, 'w') as fc:
                        if debug: print(cfg_file)
                        fc.write(cfg_data)
                    fc.close()

                    if debug:
                        print(f'\ntree_root: {tree_root}\n'
                              f'\ninput_folder: {input_folder}\n'
                              f'\niso_path: {iso_path}\n'
                              f'\nopt_path: {opt_path}\n'
                              f'\ncap_path: {cap_path}\n'
                              f'\ncell_path: {cell_path}\n'
                              f'\ncfg_file: {cfg_file}\n')
                        sys.exit()

                    filelist.append(cfg_file)

    return filelist


def run_simulations(filelist, tool_path, debug):

    run_count = 0
    for cfg_file in filelist:
        output_log = cfg_file[:-3] + "out" # strip "cfg" and replace with "txt
        if debug: print(output_log)

        sim_cmd = ""

        " cd ~/NVSim && ./nvsim ~/EXPERIMENTS/Input/Destiny/iso_capacity/Area/PCRAM/512KB/512KB.cfg >" \
        " ~/EXPERIMENTS/Input/Destiny/iso_capacity/Area/PCRAM/512KB/512KB.out"
        if re.search(r"NVSim", input_folder, re.I):
            sim_cmd = "cd " + tool_path + " && ./nvsim " + cfg_file + " > " + output_log
        elif re.search(r"Destiny", input_folder, re.I):
            sim_cmd = "cd " + tool_path + " && ./destiny " + cfg_file + " > " + output_log
        else:
            print("expecting NVsim or Destiny in the input folder path")
            sys.exit()

        print(sim_cmd); os.system(sim_cmd)
        run_count += 1; print("run count: ", run_count)


if __name__ == "__main__":

    t0 = time.perf_counter()

    args = cli_parse()

    tree_root, input_folder, tool_path, debug = setup_env(args)

    # generates all cfg files for either NVSim or Destiny
    filelist = create_cfg_files(tree_root, input_folder, debug) # calls build_cfg_data()

    # run actual simulations for either NVSim or Destiny
    run_simulations(filelist, tool_path, debug)

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