#!/usr/bin/env python3

import os
import sys
import time
import math
import argparse
import subprocess
import re
import csv
import matplotlib
# matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


global tool, HOME
HOME = os.getcwd()

# read in csv reports as dataframes
global df_nvs_2d, df_dst_2d, df_dst_hd
df_nvs_2d = pd.read_csv("NVSim_report.csv")
df_dst_2d = pd.read_csv("Destiny_report.csv")
df_dst_hd = pd.read_csv("HD_Destiny_report.csv")

# n*[0:8] =   STTRAM
# n*[9:17] =  SRAM
# n*[18:26] = RRAM
# n*[27:35] = PCRAM


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
    parser.add_argument("--parse_only", action="store_true", help="don't run simulations, only parse logs")
    parser.add_argument("--high_density", action="store_true", help="3D and MLC RRAM")
    parser.add_argument("--visualize", action="store_true", help="create plots")
    parser.add_argument("--debug", action="store_true", help="debug mode (prints paths etc.)")
    args = parser.parse_args()
    return args


def setup_env(args):
    global tree_root
    global tool

    tool = ""
    tree_root = args.tree_root
    input_folder = args.input_folder
    tool_path = args.tool_path
    parse_only = args.parse_only
    high_density = args.high_density
    visualize = args.visualize
    debug = args.debug

    if not visualize: # visualize supersedes all this checking
        if re.search(r"NVSim", input_folder, re.I):
            tool = "NVSim"
        elif re.search(r"Destiny", input_folder, re.I):
            tool = "Destiny"
        else:
            print("expecting NVsim or Destiny in the input folder path")
            sys.exit()

        for x in [ tree_root, input_folder, tool_path ]:
            path_test(x)

        print(f'\nHOME: {HOME}')
        print(f'\ntree_root: {tree_root}')
        print(f'\ninput_folder: {input_folder}')
        print(f'\ntool_path: {tool_path}\n')
        print(f'\nhigh_density: {high_density}\n')

    return tree_root, input_folder, tool_path, parse_only, high_density, visualize, debug


def build_cfg_data(opt_target, capacity, cell):

    cfg_data = ""
    if (tool == "NVSim") or (tool == "Destiny"):
        cfg_data = (f'-DesignTarget: RAM\n'
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

    else:
        print("need to enter NVSim or Destiny for cfg file generation")
        sys.exit()

    return cfg_data


def build_cfg_data_mlc(opt_target, capacity, cell):

    cfg_data = ""
    if (tool == "NVSim") or (tool == "Destiny"):
        cfg_data = (f'-DesignTarget: RAM\n'
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
                    f'-UseCactiAssumption: Yes\n'
                    f'\n'
                    f'-StackedDieCount: 1\n'
                    f'-MonolithicStackCount: 2\n\n')

    else:
        print("need to enter NVSim or Destiny for cfg file generation")
        sys.exit()

    return cfg_data


def create_cfg_files(tree_root, input_folder, parse_only, debug):

    filelist = []

    for opt_target in [ "ReadLatency", "WriteLatency", "ReadDynamicEnergy", "WriteDynamicEnergy", "ReadEDP", "WriteEDP", "LeakagePower", "Area" ]:
        opt_path = os.path.join(input_folder, opt_target)

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

                if not parse_only:
                    with open(cfg_file, 'w') as fc:
                        if debug: print(cfg_file)
                        fc.write(cfg_data)
                    fc.close()

                if debug:
                    print(f'\ntree_root: {tree_root}\n'
                          f'\ninput_folder: {input_folder}\n'
                          f'\nopt_path: {opt_path}\n'
                          f'\ncap_path: {cap_path}\n'
                          f'\ncell_path: {cell_path}\n'
                          f'\ncfg_file: {cfg_file}\n')
                    sys.exit()

                filelist.append(cfg_file)

    return filelist


def create_cfg_files_3d(tree_root, input_folder, parse_only, filelist, debug):

    for opt_target in ["ReadLatency", "WriteLatency", "ReadDynamicEnergy", "WriteDynamicEnergy", "ReadEDP", "WriteEDP", "LeakagePower", "Area"]:
        opt_path = os.path.join(input_folder, opt_target)

        for cell in ["3D_RRAM"]:
            cell_path = os.path.join(opt_path, cell)

            for capacity in ["16", "32", "64", "128", "256", "512", "1024", "2048", "4096"]:
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

                cfg_data = build_cfg_data(opt_target, capacity, cell[3:]) # "RRAM"

                if not parse_only:
                    with open(cfg_file, 'w') as fc:
                        if debug: print(cfg_file)
                        fc.write(cfg_data)
                    fc.close()

                if debug:
                    print(f'\ntree_root: {tree_root}\n'
                    f'\ninput_folder: {input_folder}\n'
                    f'\nopt_path: {opt_path}\n'
                    f'\ncap_path: {cap_path}\n'
                    f'\ncell_path: {cell_path}\n'
                    f'\ncfg_file: {cfg_file}\n')
                    sys.exit()

                filelist.append(cfg_file)

    return filelist


def create_cfg_files_mlc(tree_root, input_folder, parse_only, filelist, debug):

    for opt_target in ["ReadLatency", "WriteLatency", "ReadDynamicEnergy", "WriteDynamicEnergy", "ReadEDP", "WriteEDP", "LeakagePower", "Area"]:
        opt_path = os.path.join(input_folder, opt_target)

        for cell in ["RRAM_MLC"]:
            cell_path = os.path.join(opt_path, cell)

            for capacity in ["16", "32", "64", "128", "256", "512", "1024", "2048", "4096"]:
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

                cfg_data = build_cfg_data_mlc(opt_target, capacity, cell) # "RRAM_MLC"

                if not parse_only:
                    with open(cfg_file, 'w') as fc:
                        if debug: print(cfg_file)
                        fc.write(cfg_data)
                    fc.close()

                if debug:
                    print(f'\ntree_root: {tree_root}\n'
                    f'\ninput_folder: {input_folder}\n'
                    f'\nopt_path: {opt_path}\n'
                    f'\ncap_path: {cap_path}\n'
                    f'\ncell_path: {cell_path}\n'
                    f'\ncfg_file: {cfg_file}\n')
                    sys.exit()

                filelist.append(cfg_file)

    return filelist


def parse_output_log(output_log):
    Total_Area = Read_L = Write_L = Read_BW = Write_BW = RDE = WDE = Leakage_Power = ""

    with open(output_log, 'r') as fo:
        for line in fo:
            TA = re.search(r"Total Area\s*=\s*", line) # []m^2
            RL = re.search(r"Read (Total )?Latency\s*=\s*", line)
            WL = re.search(r"Write (Total )?Latency\s*=\s*", line)
            RB = re.search(r"Read Bandwidth\s*=\s*", line)
            WB = re.search(r"Write Bandwidth\s*=\s*", line)
            RE = re.search(r"Read Dynamic Energy\s*=\s*", line)
            WE = re.search(r"Write Dynamic Energy\s*=\s*", line)
            LP = re.search(r"Leakage Power\s*=\s*", line)

            if TA:
                result = re.match(r"^\s*-\s*Total Area\s*.*=\s*([0-9.]+)([a-z]m\^2)\s*$", line)
                if result:
                    value = result.group(1) # 102792.155
                    units = result.group(2) # um^2

                    if units[0] != "m" or units[0] != "u":
                        if units[0] == "m":  # mm^2
                            value = round(float(value) * 1000000, 3)  # 3 places past decimal point for consistency
                        Total_Area = value
                    else:
                        Total_Area = str(value) + units

            elif RL:
                result = re.match(r"^\s*-\s*Read (Total )?Latency\s*=\s*([0-9.]+)([a-z]s)\s*$", line)
                if result:
                    if not result.group(3): # Total detected
                        value = result.group(1)  # 3.407
                        units = result.group(2)  # ns
                    else:
                        value = result.group(2)  # 3.407
                        units = result.group(3)  # ns

                    if units[0] != "p" or units[0] != "n":
                        if units[0] == "p":  # ps
                            value = round(float(value) / 1000, 3)
                        Read_L = value
                    else:
                        Read_L = str(value) + units

            elif WL:
                result = re.match(r"^\s*-\s*Write (Total )?Latency\s*=\s*([0-9.]+)([a-z]s)\s*$", line)
                if result:
                    if not result.group(3):
                        value = result.group(1) # 21.855
                        units = result.group(2) # ns
                    else:
                        value = result.group(2) # 21.855
                        units = result.group(3) # ns

                    if units[0] != "p" or units[0] != "n":
                        if units[0] == "p":  # ps
                            value = round(float(value) / 1000, 3)
                        Write_L = value
                    else:
                        Write_L = str(value) + units

            elif RB:
                result = re.match(r"^\s*-\s*Read Bandwidth\s*=\s*([0-9.]+)([A-Z]B/s)\s*$", line)
                if result:
                    value = result.group(1) # 3.948
                    units = result.group(2) # GB/s

                    if units[0] != "M" or units[0] != "G":
                        if units[0] == "M":  # MB/s
                            value = round(float(value) / 1000, 3)
                        Read_BW = value
                    else:
                        Read_BW = str(value) + units

            elif WB:
                result = re.match(r"^\s*-\s*Write Bandwidth\s*=\s*([0-9.]+)([A-Z]B/s)\s*$", line)
                if result:
                    value = result.group(1) # 744.882
                    units = result.group(2) # MB/s

                    if units[0] != "M" or units[0] != "G":
                        if units[0] == "M":  # MB/s
                            value = round(float(value) / 1000, 3)
                        Write_BW = value
                    else:
                        Write_BW = str(value) + units

            elif RE:
                result = re.match(r"^\s*-\s*Read Dynamic Energy\s*=\s*([0-9.]+)([a-z]J)\s*$", line)
                if result:
                    value = result.group(1) # 105.772
                    units = result.group(2) # pJ

                    if units[0] != "p" or units[0] != "n":
                        if units[0] == "n":  # nJ
                            value = round(float(value) * 1000, 3)
                        RDE = value
                    else:
                        RDE = str(value) + units

            elif WE:
                result = re.match(r"^\s*-\s*Write Dynamic Energy\s*=\s*([0-9.]+)([a-z]J)\s*$", line)
                if result:
                    value = result.group(1) # 187.673
                    units = result.group(2) # pJ

                    if units[0] != "n" or units[0] != "p":
                        if units[0] == "n":  # nJ
                            value = round(float(value) * 1000, 3)
                        WDE = value
                    else:
                        WDE = str(value) + units

            elif LP:
                result = re.match(r"^\s*-\s*Leakage Power\s*=\s*([0-9.]+)([a-z]W)\s*$", line)
                if result:
                    value = result.group(1) # 61.128
                    units = result.group(2) # uW

                    if units[0] != "m" or units[0] != "u":
                        if units[0] == "m":  # mW
                            value = round(float(value) * 1000, 3)
                        Leakage_Power = value
                    else:
                        Leakage_Power = str(value) + units

    fo.close()

    sim_settings = ':'.join(output_log.split('/')[-5:-1])
    # fields = [ sim_settings, Total_Area, Read_L, Write_L, Read_BW, Write_BW, RDE, WDE, Leakage_Power ]

    tool, opt_target, cell, size = output_log.split('/')[-5:-1]
    fields = [ tool, opt_target, cell, size.split('KB')[0],
               Total_Area, Read_L, Write_L, Read_BW, Write_BW, RDE, WDE, Leakage_Power ]

    return fields

    """
     - Total Area = 114.881um x 894.774um = 102792.155um^2
     -  Read Latency = 3.407ns
      - Write Latency = 21.855ns
       - Read Bandwidth  = 3.948GB/s
     - Write Bandwidth = 744.882MB/s
     -  Read Dynamic Energy = 105.772pJ
     - Write Dynamic Energy = 187.673pJ
      - Leakage Power = 61.128uW
  """


def run_simulations(filelist, tool_path, parse_only, high_density, debug):

    if parse_only: # add csv headers
        suffix = ""
        if tool == "Destiny" and high_density:
            suffix = "HD_" + tool + "_report.csv"
        else:
            suffix = tool + "_report.csv"
        csv_report = os.path.join(tree_root, suffix)
        if os.path.exists(csv_report):
            os.remove(csv_report)

        with open(csv_report, 'a+', encoding='ascii', newline='\n') as csvfile:
            header = [ 'Tool', 'Optimization Target', 'Cell Type', 'Capacity (KB)',
                       'Total Area (um^2)', 'Read Latency (ns)', 'Write Latency (ns)',
                       'Read Bandwidth (GB/s)', 'Write Bandwidth (GB/s)',
                       'Read Dynamic Energy (pJ)', 'Write Dynamic Energy (pJ)', 'Leakage Power (uW)' ]
            writer = csv.DictWriter(csvfile, fieldnames=header)
            writer.writeheader()
        csvfile.close()

    output_log_list = []

    run_count = 0
    for cfg_file in filelist:
        output_log = cfg_file[:-3] + "out" # strip "cfg" and replace with "txt

        output_log_list.append(str(output_log))

        if debug: print(output_log)

        sim_cmd = ""
        if tool == "NVSim":
            sim_cmd = "cd " + tool_path + " && ./nvsim " + cfg_file + " > " + output_log
        elif tool == "Destiny":
            sim_cmd = "cd " + tool_path + " && ./destiny " + cfg_file + " > " + output_log

        if not parse_only: # generate
            print(sim_cmd); os.system(sim_cmd)

        else: # parse only
            fields = parse_output_log(output_log)

            with open(csv_report, 'a+', encoding='ascii', newline='\n') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(fields)
                print(output_log)
            csvfile.close()

        run_count += 1; print("run count: ", run_count)

    if parse_only:
        print("csv_report: ", csv_report)


# set type to any plot type in the seaborn reference: https://seaborn.pydata.org/api.html
def graph(plot_type, xax, yax, df): # unused helper
    ax = getattr(sns, plot_type)(x=xax, y=yax, data=df)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right")
    plt.rcParams["xtick.labelsize"] = 7
    plt.xlabel(xax); plt.ylabel(yax)
    plt.title(xax + " vs " + yax)
    plt.tight_layout(); plt.show()


# expects 36 row dataframe
def plot_4x2_boxplot(dataframe, xaxis, title, cell_type=None, savefile=None, show=False): # helper function
    if len(dataframe) % 9 != 0:
        print(f'\nexpecting dataframe lengths in multiples of 9\n'); sys.exit(-1)
    if cell_type == 'STTRAM':
        dataframe = dataframe.loc[0:8]
    elif cell_type == 'SRAM':
        dataframe = dataframe.loc[9:17]
    elif cell_type == 'RRAM':
        dataframe = dataframe.loc[18:26]
    elif cell_type == 'PCRAM':
        dataframe = dataframe.loc[27:35]

    if cell_type is not None: title = f'{cell_type}: {title}'

    fig, axes = plt.subplots(4, 2, figsize=(24, 18))
    fig.suptitle(f'{title}')

    # sns.boxplot(ax=axes[0, 0], data=dataframe, x=f'{xaxis}', y='Total Area (um^2)', labels=['STTRAM', 'SRAM', 'RRAM', 'PCRAM'])
    sns.boxplot(ax=axes[0, 0], data=dataframe, x=f'{xaxis}', y='Total Area (um^2)')
    sns.boxplot(ax=axes[0, 1], data=dataframe, x=f'{xaxis}', y='Leakage Power (uW)')
    sns.boxplot(ax=axes[1, 0], data=dataframe, x=f'{xaxis}', y='Read Latency (ns)')
    sns.boxplot(ax=axes[1, 1], data=dataframe, x=f'{xaxis}', y='Write Latency (ns)')
    sns.boxplot(ax=axes[2, 0], data=dataframe, x=f'{xaxis}', y='Read Bandwidth (GB/s)')
    sns.boxplot(ax=axes[2, 1], data=dataframe, x=f'{xaxis}', y='Write Bandwidth (GB/s)')
    sns.boxplot(ax=axes[3, 0], data=dataframe, x=f'{xaxis}', y='Read Dynamic Energy (pJ)')
    sns.boxplot(ax=axes[3, 1], data=dataframe, x=f'{xaxis}', y='Write Dynamic Energy (pJ)')

    if savefile: plt.savefig(savefile)
    if show: plt.show()

def plot_and_save(opt_targets: dict): # helper function
    # create 8 plots for each result metric, for each optimization target
    for opt_type, df in opt_targets.items():
        save_fig = (opt_type.split(':')[0]).replace(' ', '') + '_OptTgt_' + (
            opt_type.split(':')[2].replace(' ', '')) + '.png'
        plot_4x2_boxplot(df, 'Capacity (KB)', opt_type, savefile=save_fig, show=False)


def create_plots(sheet):

    if sheet == "DESTINY 2D":
        # destiny 2D with 8 optimizations
        df_dst_2d_opt_r_lat = df_dst_2d.loc[0:35]
        df_dst_2d_opt_w_lat = df_dst_2d.loc[36:71]
        df_dst_2d_opt_rde =   df_dst_2d.loc[72:107]
        df_dst_2d_opt_wde =   df_dst_2d.loc[108:143]
        df_dst_2d_opt_r_edp = df_dst_2d.loc[144:179]
        df_dst_2d_opt_w_edp = df_dst_2d.loc[180:215]
        df_dst_2d_opt_l_pow = df_dst_2d.loc[216:251]
        df_dst_2d_opt_area =  df_dst_2d.loc[252:287]

        opt_targets = {'Destiny 2D: Optimization Target: Area':                       df_dst_2d_opt_area,
                       'Destiny 2D: Optimization Target: Leakage Power':              df_dst_2d_opt_l_pow,
                       'Destiny 2D: Optimization Target: Read Latency':               df_dst_2d_opt_r_lat,
                       'Destiny 2D: Optimization Target: Write Latency':              df_dst_2d_opt_w_lat,
                       'Destiny 2D: Optimization Target: Read Dynamic Energy':        df_dst_2d_opt_rde,
                       'Destiny 2D: Optimization Target: Write Dynamic Energy':       df_dst_2d_opt_wde,
                       'Destiny 2D: Optimization Target: Read Energy Delay Product':  df_dst_2d_opt_r_edp,
                       'Destiny 2D: Optimization Target: Write Energy Delay Product': df_dst_2d_opt_w_edp, }

        plot_and_save(opt_targets)

    elif sheet == "NVSIM 2D":
        # nvsim 2D with 8 optimizations
        df_nvs_opt_r_lat = df_nvs_2d.loc[0:35]
        df_nvs_opt_w_lat = df_nvs_2d.loc[36:71]
        df_nvs_opt_rde = df_nvs_2d.loc[72:107]
        df_nvs_opt_wde = df_nvs_2d.loc[108:143]
        df_nvs_opt_r_edp = df_nvs_2d.loc[144:179]
        df_nvs_opt_w_edp = df_nvs_2d.loc[180:215]
        df_nvs_opt_l_pow = df_nvs_2d.loc[216:251]
        df_nvs_opt_area = df_nvs_2d.loc[252:287]

        opt_targets = {'NVSim 2D: Optimization Target: Area':                       df_nvs_opt_area,
                       'NVSim 2D: Optimization Target: Leakage Power':              df_nvs_opt_l_pow,
                       'NVSim 2D: Optimization Target: Read Latency':               df_nvs_opt_r_lat,
                       'NVSim 2D: Optimization Target: Write Latency':              df_nvs_opt_w_lat,
                       'NVSim 2D: Optimization Target: Read Dynamic Energy':        df_nvs_opt_rde,
                       'NVSim 2D: Optimization Target: Write Dynamic Energy':       df_nvs_opt_wde,
                       'NVSim 2D: Optimization Target: Read Energy Delay Product':  df_nvs_opt_r_edp,
                       'NVSim 2D: Optimization Target: Write Energy Delay Product': df_nvs_opt_w_edp, }

        plot_and_save(opt_targets)

    elif sheet == "DESTINY HD":
        # destiny High Density with 8 optimizations

        # 3D RRAM
        df_dst_3d_opt_r_lat = df_dst_hd.loc[0:8]
        df_dst_3d_opt_w_lat = df_dst_hd.loc[9:17]
        df_dst_3d_opt_rde = df_dst_hd.loc[18:26]
        df_dst_3d_opt_wde = df_dst_hd.loc[27:35]
        df_dst_3d_opt_r_edp = df_dst_hd.loc[36:44]
        df_dst_3d_opt_w_edp = df_dst_hd.loc[45:53]
        df_dst_3d_opt_l_pow = df_dst_hd.loc[54:62]
        df_dst_3d_opt_area = df_dst_hd.loc[63:71]

        opt_targets = {'Destiny 3D: Optimization Target: Area':                       df_dst_3d_opt_area,
                       'Destiny 3D: Optimization Target: Leakage Power':              df_dst_3d_opt_l_pow,
                       'Destiny 3D: Optimization Target: Read Latency':               df_dst_3d_opt_r_lat,
                       'Destiny 3D: Optimization Target: Write Latency':              df_dst_3d_opt_w_lat,
                       'Destiny 3D: Optimization Target: Read Dynamic Energy':        df_dst_3d_opt_rde,
                       'Destiny 3D: Optimization Target: Write Dynamic Energy':       df_dst_3d_opt_wde,
                       'Destiny 3D: Optimization Target: Read Energy Delay Product':  df_dst_3d_opt_r_edp,
                       'Destiny 3D: Optimization Target: Write Energy Delay Product': df_dst_3d_opt_w_edp, }

        plot_and_save(opt_targets)

        # MLC RRAM
        df_dst_mlc_opt_r_lat = df_dst_hd.loc[72:80]
        df_dst_mlc_opt_w_lat = df_dst_hd.loc[81:89]
        df_dst_mlc_opt_rde = df_dst_hd.loc[90:98]
        df_dst_mlc_opt_wde = df_dst_hd.loc[99:107]
        df_dst_mlc_opt_r_edp = df_dst_hd.loc[108:116]
        df_dst_mlc_opt_w_edp = df_dst_hd.loc[117:125]
        df_dst_mlc_opt_l_pow = df_dst_hd.loc[126:134]
        df_dst_mlc_opt_area = df_dst_hd.loc[135:143]
        
        opt_targets = {'Destiny MLC: Optimization Target: Area':                       df_dst_mlc_opt_area,
                       'Destiny MLC: Optimization Target: Leakage Power':              df_dst_mlc_opt_l_pow,
                       'Destiny MLC: Optimization Target: Read Latency':               df_dst_mlc_opt_r_lat,
                       'Destiny MLC: Optimization Target: Write Latency':              df_dst_mlc_opt_w_lat,
                       'Destiny MLC: Optimization Target: Read Dynamic Energy':        df_dst_mlc_opt_rde,
                       'Destiny MLC: Optimization Target: Write Dynamic Energy':       df_dst_mlc_opt_wde,
                       'Destiny MLC: Optimization Target: Read Energy Delay Product':  df_dst_mlc_opt_r_edp,
                       'Destiny MLC: Optimization Target: Write Energy Delay Product': df_dst_mlc_opt_w_edp, }

        plot_and_save(opt_targets)

    else:
        print('\nSheet not found, please review code\n')
        sys.exit(-1)


def graph_multi_compare(df, opt_target, count, xname, yname, log=False, show=False, save=False):
    df = df.reset_index().melt(f'{xname}', var_name='', value_name='vals')
    df = df.iloc[9:, :]  # trim off bad index rows

    g = sns.catplot(x=f'{xname}', y="vals", hue='', data=df, kind='bar', legend=False, height=3.5, aspect=15 / 8)
    g.set(title=f'{xname} vs {yname}\n\nOptimization Target: [{opt_target}]')
    g.set(xlabel=f'{xname}', ylabel=f'{yname}')
    # plt.ticklabel_format(style='plain', axis='y')

    plt.rcParams["axes.titlesize"] = 10
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={"size": 7})

    if log:
        plt.yscale('log')
    plt.tight_layout()

    if show: plt.show()
    if save:
        opt_tgt = opt_target.replace(' ', '')
        plt.savefig(f'RRAM_OptTgt_{opt_tgt}_{count}.png')


def form_dataframe_4way(indices, xname, yname):
    # Read Latency Optimized - RRAM cells
    xaxis = df_nvs_2d.loc[indices[0]:indices[0] + 8][xname]  # 16 - 4096 KB
    df0 =   df_nvs_2d.loc[indices[0]:indices[0] + 8][yname]  # SLC RRAM NVS
    df1 =   df_dst_2d.loc[indices[0]:indices[0] + 8][yname]  # SLC RRAM DST
    df2 =   df_dst_hd.loc[indices[1]:indices[1] + 8][yname]  # 3D  RRAM DST
    df3 =   df_dst_hd.loc[indices[2]:indices[2] + 8][yname]  # MLC RRAM DST
    # drop removes Nan values
    df = pd.concat([xaxis.reset_index(drop=True), df0.reset_index(drop=True), df1.reset_index(drop=True),
                    df2.reset_index(drop=True), df3.reset_index(drop=True)], ignore_index=True, join="outer", axis=1)
    # headers
    df.columns = ["Capacity (KB)", "NVSim 2D SLC RRAM", "Destiny 2D SLC RRAM", "Destiny 3D RRAM", "Destiny MLC RRAM"]
    return df


def form_dataframe_3way(indices, xname, yname): # does not include MLC RRAM (does not have R/W BW result)
    # Read Latency Optimized - RRAM cells
    xaxis = df_nvs_2d.loc[indices[0]:indices[0] + 8][xname]  # 16 - 4096 KB
    df0 =   df_nvs_2d.loc[indices[0]:indices[0] + 8][yname]  # SLC RRAM NVS
    df1 =   df_dst_2d.loc[indices[0]:indices[0] + 8][yname]  # SLC RRAM DST
    df2 =   df_dst_hd.loc[indices[1]:indices[1] + 8][yname]  # 3D  RRAM DST
    # df3 =   df_dst_hd.loc[indices[2]:indices[2] + 8][yname]  # MLC RRAM DST   # does not have R/W BW result
    # drop removes Nan values
    df = pd.concat([xaxis.reset_index(drop=True), df0.reset_index(drop=True), df1.reset_index(drop=True),
                    df2.reset_index(drop=True)], ignore_index=True, join="outer", axis=1)
    # headers
    df.columns = ["Capacity (KB)", "NVSim 2D SLC RRAM", "Destiny 2D SLC RRAM", "Destiny 3D RRAM"]
    return df


def rram_multi_comparison(option):
    # 0:8, 9:17, 18:26, 27:35;  36:44, 45:53, 54:62, 63:71
    opt_targets = {'Read Latency':               [18, 0, 72],
                   'Write Latency':              [54, 9, 81],
                   'Read Dynamic Energy':        [90, 18, 90],
                   'Write Dynamic Energy':       [126, 27, 99],
                   'Read Energy Delay Product':  [162, 36, 108],
                   'Write Energy Delay Product': [198, 45, 117],
                   'Leakage Power':              [234, 54, 126],
                   'Area':                       [270, 63, 135]}

    count = 0

    if option == "4way":
        # Read Bandwidth (GB/s) and Write Bandwidth (GB/s) not recorded for MLC RRAM, so excluding from comparisons
        for y_var_result in ['Total Area (um^2)', 'Read Latency (ns)', 'Write Latency (ns)', 'Read Dynamic Energy (pJ)',
                       'Write Dynamic Energy (pJ)', 'Leakage Power (uW)']:
            for opt_target, indices in opt_targets.items(): # 48 graphs with capacity as fixed X value
                for x_var_result in ["Capacity (KB)"]:
                    df = form_dataframe_4way(indices, xname=x_var_result, yname=y_var_result)
                    graph_multi_compare(df, opt_target, count, xname=x_var_result, yname=y_var_result, log=False, save=True)
                    count += 1

    elif option == "3way":
        for y_var_result in ['Read Bandwidth (GB/s)', 'Write Bandwidth (GB/s)']: # exclude 3D RRAM
            for opt_target, indices in opt_targets.items(): # 16 graphs with capacity as fixed X value
                for x_var_result in ["Capacity (KB)"]:
                    df = form_dataframe_3way(indices, xname=x_var_result, yname=y_var_result)
                    graph_multi_compare(df, opt_target, count, xname=x_var_result, yname=y_var_result, log=False, save=True)
                    count += 1


def form_dataframe_2d(indices, xname, yname):
    # Read Latency Optimized - RRAM cells
    xaxis = df_nvs_2d.loc[indices[0]:indices[0] + 8][xname]  # 16 - 4096 KB
    df0 = df_nvs_2d.loc[indices[0]:indices[0] + 8][yname]  # SLC STTRAM NVS
    df1 = df_dst_2d.loc[indices[0]:indices[0] + 8][yname]  # SLC STTRAM DST
    df2 = df_nvs_2d.loc[indices[0] + 9*1:indices[0] + 9*1 + 8][yname]  # SLC SRAM NVS
    df3 = df_dst_2d.loc[indices[0] + 9*1:indices[0] + 9*1 + 8][yname]  # SLC SRAM DST
    df4 = df_nvs_2d.loc[indices[0] + 9*2:indices[0] + 9*2 + 8][yname]  # SLC RRAM NVS
    df5 = df_dst_2d.loc[indices[0] + 9*2:indices[0] + 9*2 + 8][yname]  # SLC RRAM DST

    # print(df0, df2, df4)
    # drop removes Nan values
    df = pd.concat([xaxis.reset_index(drop=True), df0.reset_index(drop=True), df1.reset_index(drop=True),
                    df2.reset_index(drop=True), df3.reset_index(drop=True), df4.reset_index(drop=True),
                    df5.reset_index(drop=True)], ignore_index=True, join="outer", axis=1)
    # print(df)
    # headers
    df.columns = ["Capacity (KB)", "NVSim 2D SLC STTRAM", "Destiny 2D SLC STTRAM", "NVSim 2D SLC SRAM",
                  "Destiny 2D SLC SRAM", "NVSim 2D SLC RRAM", "Destiny 2D SLC RRAM" ]
    return df


def comparison_2d(): # exclude PCRAM because NVSim didn't record it
    opt_targets = {'Read Latency':               [0],
                   'Write Latency':              [36],
                   'Read Dynamic Energy':        [72],
                   'Write Dynamic Energy':       [108],
                   'Read Energy Delay Product':  [144],
                   'Write Energy Delay Product': [180],
                   'Leakage Power':              [216],
                   'Area':                       [252]}

    count = 0
    # STTRAM SRAM RRAM   between NVSim and Destiny
    for y_var_result in ['Total Area (um^2)', 'Read Latency (ns)', 'Write Latency (ns)', 'Read Bandwidth (GB/s)',
                         'Write Bandwidth (GB/s)', 'Read Dynamic Energy (pJ)', 'Write Dynamic Energy (pJ)', 'Leakage Power (uW)']:
        for opt_target, indices in opt_targets.items():  # 48 graphs with capacity as fixed X value
            for x_var_result in ["Capacity (KB)"]:
                df = form_dataframe_2d(indices, xname=x_var_result, yname=y_var_result)
                graph_multi_compare(df, opt_target, count, xname=x_var_result, yname=y_var_result, log=True, save=True)
                count += 1


if __name__ == "__main__":

    t0 = time.perf_counter()

    args = cli_parse()

    tree_root, input_folder, tool_path, parse_only, high_density, visualize, debug = setup_env(args)

    filelist = []

    if not visualize:

        if not high_density:
            # generates all cfg files for either NVSim or Destiny
            filelist = create_cfg_files(tree_root, input_folder, parse_only, debug) # calls build_cfg_data()

        if tool == "Destiny" and high_density:

            filelist = create_cfg_files_3d(tree_root, input_folder, parse_only, filelist, debug) # calls build_cfg_data()

            filelist = create_cfg_files_mlc(tree_root, input_folder, parse_only, filelist, debug) # calls build_cfg_data_mlc()

        # run actual simulations for either NVSim or Destiny
        run_simulations(filelist, tool_path, parse_only, high_density, debug)

    else:
        # create graphs of results and saves figures
        # for sheet_name in [ "DESTINY 2D", "NVSIM 2D", "DESTINY HD" ]: create_plots(sheet_name)
        # create_plots("DESTINY 2D")
        # create_plots("NVSIM 2D")
        # create_plots("DESTINY HD")

        # rram_multi_comparison(option="3way") # "3way", "4way"
        rram_multi_comparison(option="4way") # "3way", "4way"

        # comparison_2d()

    t1 = time.perf_counter()

    pretty_time(t0, t1)

    sys.exit()


# sample of how to run in dir:
# /Users/sudo/CodeProjects/Tufts/EECE0193/Final_Project/EXPERIMENTS/

# NVSim - run simulations + generate reports
# python3 ../EXPERIMENTS/file_gen.py --tree_root /Users/sudo/CodeProjects/Tufts/EECE0193/Final_Project/EXPERIMENTS
# --if /Users/sudo/CodeProjects/Tufts/EECE0193/Final_Project/EXPERIMENTS/Input/NVSim
# --tool_path /Users/sudo/CodeProjects/Tufts/EECE0193/Final_Project/NVSim

# NVSim - parse sim reports
# python3 ../EXPERIMENTS/file_gen.py --tree_root /Users/sudo/CodeProjects/Tufts/EECE0193/Final_Project/EXPERIMENTS
# --if /Users/sudo/CodeProjects/Tufts/EECE0193/Final_Project/EXPERIMENTS/Input/NVSim
# --tool_path /Users/sudo/CodeProjects/Tufts/EECE0193/Final_Project/NVSim --parse_only

# Destiny - run simulations + generate reports
# python3 ../EXPERIMENTS/file_gen.py --tree_root /Users/sudo/CodeProjects/Tufts/EECE0193/Final_Project/EXPERIMENTS
# --if /Users/sudo/CodeProjects/Tufts/EECE0193/Final_Project/EXPERIMENTS/Input/Destiny
# --tool_path /Users/sudo/CodeProjects/Tufts/EECE0193/Final_Project/destiny_v2

# Destiny - parse sim reports
# python3 ../EXPERIMENTS/file_gen.py --tree_root /Users/sudo/CodeProjects/Tufts/EECE0193/Final_Project/EXPERIMENTS
# --if /Users/sudo/CodeProjects/Tufts/EECE0193/Final_Project/EXPERIMENTS/Input/Destiny
# --tool_path /Users/sudo/CodeProjects/Tufts/EECE0193/Final_Project/destiny_v2 --parse_only

# Destiny - run simulations + generate reports (3D and MLC)
# python3 file_gen.py --tree_root /Users/sudo/CodeProjects/Tufts/EECE0193/Final_Project/EXPERIMENTS
# --if /Users/sudo/CodeProjects/Tufts/EECE0193/Final_Project/EXPERIMENTS/Input/Destiny
# --tool_path /Users/sudo/CodeProjects/Tufts/EECE0193/Final_Project/destiny_v2 --high_density

# Destiny - parse sim reports (3D and MLC)
# python3 file_gen.py --tree_root /Users/sudo/CodeProjects/Tufts/EECE0193/Final_Project/EXPERIMENTS
# --if /Users/sudo/CodeProjects/Tufts/EECE0193/Final_Project/EXPERIMENTS/Input/Destiny
# --tool_path /Users/sudo/CodeProjects/Tufts/EECE0193/Final_Project/destiny_v2 --high_density --parse_only

###################################################################################################################


"""
    plt.style.use('_mpl-gallery')

    # make the data
    np.random.seed(3)
    x = 4 + np.random.normal(0, 2, 24)
    y = 4 + np.random.normal(0, 2, len(x))
    # size and color:
    sizes = np.random.uniform(15, 80, len(x))
    colors = np.random.uniform(15, 80, len(x))

    # plot
    fig, ax = plt.subplots()

    ax.scatter(x, y, s=sizes, c=colors, vmin=0, vmax=100)

    ax.set(xlim=(0, 8), xticks=np.arange(1, 8),
           ylim=(0, 8), yticks=np.arange(1, 8))

    plt.show()

"""


""" parameters that change for each dir / test
-OptimizationTarget: [ ReadLatency, WriteLatency, ReadDynamicEnergy, WriteDynamicEnergy, ReadEDP, WriteEDP, LeakagePower, Area]
-Capacity (KB): [ 16, 32, 64, 128, 256, 512, 1024, 2048, 4096 ]
-MemoryCellInputFile: ./cell_defs/SRAM.cell
"""


"""
User-defined configuration file (/Users/sudo/CodeProjects/Tufts/EECE0193/Final_Project/EXPERIMENTS/Input/NVSim/iso_area/LeakagePower/RRAM/2048KB/2048KB.cfg) is loaded

Memory Cell: RRAM (Memristor)
Cell Area (F^2)    : 4.000 (2.000Fx2.000F)
Cell Aspect Ratio  : 1.000
Cell Turned-On Resistance : 1.000Mohm
Cell Turned-Off Resistance: 10.000Mohm
Read Mode: Current-Sensing
  - Read Voltage: 0.400V
Reset Mode: Voltage
  - Reset Voltage: 2.000V
  - Reset Pulse: 10.000ns
Set Mode: Voltage
  - Set Voltage: 2.000V
  - Set Pulse: 10.000ns
Access Type: None Access Device

====================
DESIGN SPECIFICATION
====================
Design Target: Random Access Memory
Capacity   : 2MB
Data Width : 128Bits (16Bytes)

Searching for the best solution that is optimized for leakage power ...

=============
   RESULT
=============
Area:
 - Total Area = 114.881um x 894.774um = 102792.155um^2
 |--- Mat Area      = 57.440um x 111.847um = 6424.510um^2   (31.598%)
 |--- Subarray Area = 28.720um x 51.568um = 1481.040um^2   (34.267%)
 - Area Efficiency = 31.598%
Timing:
 -  Read Latency = 3.407ns
 |--- H-Tree Latency = 361.162ps
 |--- Mat Latency    = 3.046ns
    |--- Predecoder Latency = 194.830ps
    |--- Subarray Latency   = 2.851ns
       |--- Row Decoder Latency = 208.904ps
       |--- Bitline Latency     = 35.803ps
       |--- Senseamp Latency    = 1.454ns
       |--- Mux Latency         = 75.472ps
       |--- Precharge Latency   = 1.410ns
 - Write Latency = 21.855ns
 |--- H-Tree Latency = 180.581ps
 |--- Mat Latency    = 21.675ns
    |--- Predecoder Latency = 194.830ps
    |--- Subarray Latency   = 21.480ns
       |--- Row Decoder Latency = 208.904ps
       |--- Charge Latency      = 96.881ps
 - Read Bandwidth  = 3.948GB/s
 - Write Bandwidth = 744.882MB/s
Power:
 -  Read Dynamic Energy = 105.772pJ
 |--- H-Tree Dynamic Energy = 24.225pJ
 |--- Mat Dynamic Energy    = 10.193pJ per mat
    |--- Predecoder Dynamic Energy = 0.046pJ
    |--- Subarray Dynamic Energy   = 2.537pJ per active subarray
       |--- Row Decoder Dynamic Energy = 0.045pJ
       |--- Mux Decoder Dynamic Energy = 1.678pJ
       |--- Bitline & Cell Read Energy = 0.002pJ
       |--- Senseamp Dynamic Energy    = 0.601pJ
       |--- Mux Dynamic Energy         = 0.024pJ
       |--- Precharge Dynamic Energy   = 0.186pJ
 - Write Dynamic Energy = 187.673pJ
 |--- H-Tree Dynamic Energy = 24.225pJ
 |--- Mat Dynamic Energy    = 20.431pJ per mat
    |--- Predecoder Dynamic Energy = 0.046pJ
    |--- Subarray Dynamic Energy   = 5.096pJ per active subarray
       |--- Row Decoder Dynamic Energy = 0.045pJ
       |--- Mux Decoder Dynamic Energy = 1.678pJ
       |--- Mux Dynamic Energy         = 0.024pJ
 - Leakage Power = 61.128uW
 |--- H-Tree Leakage Power = 0.000pW
 |--- Mat Leakage Power    = 3.820uW per mat

Finished!

:return:
"""
