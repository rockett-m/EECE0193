#!/usr/bin/env python3

import os
import sys
import time
import math
import argparse
import subprocess
import re
import csv


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


def create_cache_files():

    sample_cache = os.path.join(cache_path, "SRAM_cache.cfg")

    for cap in [16, 32, 64, 128, 256, 512, 1024, 2048]:  # 16kB to 2MB cache size

        for assoc in [1, 2, 4, 8, 16]:  # 1 to 16 way associative

            gen_file = f'SRAM_cache_{cap}_{assoc}.cfg'
            output_file = os.path.join(cache_path, gen_file)
            with open(output_file, 'w') as fo:

                with open(sample_cache, 'r') as fi:
                    for line in fi: # sample_cache

                        result_cap = re.match(r"(-Capacity\s\(KB\): )(\d+)(\s*)", line)
                        result_assoc = re.match(r"(-Associativity\s\(for cache only\): )(\d+)(\s*)", line)

                        if result_cap:
                            capacity = result_cap.group(1) + str(cap) + result_cap.group(3)
                            fo.write(capacity)
                        elif result_assoc:
                            associativity = result_assoc.group(1) + str(assoc) + result_assoc.group(3)
                            fo.write(associativity)
                        else:
                            fo.write(line)

                fi.close()

            fo.close()


def run_nvsim():

    nvsim_path = os.path.realpath("nvsim")
    # print("\nnvsim_path:\n\t", nvsim_path)
    path_test(nvsim_path)

    for root, dirs, files in os.walk(cache_path):
        # print("root", root)
        for file in files: # cache file
            if re.search(r".cfg", file): # cfg files only

                output = file.split('.cfg')[0] + ".out"
                output_file = os.path.join(cache_path, output)

                full_file = os.path.join(cache_path, file)

                if not os.path.exists(output_file):
                    try:
                        cmd = f'{nvsim_path} {full_file} > {output_file}'
                        print("\nnvsim cmd:\n\t", cmd)
                        shell_exec(cmd)
                        print("\ncache results:\n\t", output_file)
                    except:
                        print("\ncouldn't execute nv sim cmd\n")

                else: # file size test
                    cmd_size = "ls -l " + output_file + " | awk '{print $5}'"
                    size = shell_exec(cmd_size)[0]
                    if int(size) < 6000:
                        try:
                            cmd = f'{nvsim_path} {full_file} > {output_file}'
                            print("\nnvsim cmd:\n\t", cmd)
                            shell_exec(cmd)
                            print("\ncache results:\n\t", output_file)
                        except:
                            print("\ncouldn't execute nv sim cmd\n")
            else:
                pass


def send_to_csv():

    struct = []

    for root, dirs, files in os.walk(cache_path):
        # print("root", root)
        for file in files: # cache file
            if re.search(r".out", file): # out files only

                data = []

                configuration = file.split('.out')[0] # size + assoc
                data.append(configuration)

                results_file = os.path.join(cache_path, file)
                with open(results_file, 'r') as fo:

                    for line in fo:
                        read_access_time_result = re.match(r"( - Cache Hit Latency )\s*=\s*([0-9a-z.]+)(\s*)", line)
                        read_energy_result = re.match(r"( - Cache Hit Dynamic Energy )\s*\=\s*([0-9a-zA-Z.]+)( per access\s*)", line)

                        access_time = ""; read_energy = ""

                        if read_access_time_result:
                            access_time = read_access_time_result.group(2)[:-2]
                            data.append(access_time)
                        elif read_energy_result:
                            read_energy = read_energy_result.group(2)[:-2]
                            data.append(read_energy)
                        else:
                            pass

                    struct.append(data)
                fo.close()

    return struct


def write_csv(struct):

    data_file = os.path.join(cache_path, "data.csv")
    with open(data_file, 'w') as fd:

        csvwriter = csv.writer(fd, quotechar='"', escapechar='\\')

        headers = ["cache size(KB) and associativity", "read access time (ns)", "read energy (nJ)"]
        csvwriter.writerow(headers)

        for line in struct:
            csvwriter.writerow(line)
            # print(line)

    fd.close()

    print(f'\ncsv file written: {data_file}\n')


if __name__ == "__main__":

    t0 = time.perf_counter()

    args = cli_parse()

    setup(args)

    # create_cache_files()

    # run_nvsim()

    struct = send_to_csv()

    write_csv(struct)

    t1 = time.perf_counter()

    pretty_time(t0, t1)