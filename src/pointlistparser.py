#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import argparse
import codecs
import logging

logging.basicConfig(filename='pointlistparser.log',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(lineno)d - %(message)s')

logging.debug('#' * 50)
logging.debug('----   ---   start processing   ----   ---')

version = '0.01'
# default script params
def_parms = dict(input_fn='PNT5011.NDL',
                 out_fn='PNT5011.parsed.TXT')

# getting script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
logging.debug('script directory is %s' % script_dir)

logging.debug('Script version is %s' % version)

# Look at command-line args
parser = argparse.ArgumentParser(description='This script parse pointlist at separate file.')

parser.add_argument('--input', '-i', type=str,
                    default='PNT5011.NDL',
                    help='Input file name. \
                    Default value is "PNT5011.NDL"')

parser.add_argument('--out', '-o', type=str,
                    default='PNT5011.parsed.TXT',
                    help='Output file name. \
                    Default value is "PNT5011.parsed.TXT"')

args = parser.parse_args()

logging.debug("params are %s after command line args processing" % args)


logging.debug('----   ---   start working   ----   ---')

result_list = []
boss_address = ''

with codecs.open(args.input, "r", "utf-8") as pnt_file_in:
    for single_line in pnt_file_in:
        single_line = single_line.rstrip()
        if single_line[0] == ';':
            if ';Point,' in single_line:
                single_line = single_line[1::]
            else:
                continue
        if 'Boss,2:5011/' in single_line:
            boss_split = single_line.split(',')
            boss_address = boss_split[1]
            continue

        splitted_pointline = single_line.split(',')

        if len(splitted_pointline) < 4:
            continue

        point_num = splitted_pointline[1]
        point_name = splitted_pointline[4].replace('_', ' ')

        result_line = boss_address + '.' + point_num + ',' + point_name

        result_list.append(result_line)

print("Saving results..")
try:
    with codecs.open(args.out, "w", "utf-8") as file_out:
        for single_line in result_list:
            single_line += "\n"
            file_out.write(single_line)

except Exception as e:
    print("Error while opening {}".format(args.out))
    raise e

print("Done")
