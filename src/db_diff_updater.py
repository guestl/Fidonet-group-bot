# -*- coding: utf-8 -*-

# helper for work with database
import sqlite3

import config
import argparse
import codecs

import os
from shutil import copyfile


# I got this piece of code from
#    http://stackoverflow.com/questions/5266430/how-to-see-the-real-sql-query-in-python-cursor-execute"
# it doesn't work pretty good,
#   but I can see a sql text and it's enough for me
def check_sql_string(self, sql_text, values):
    unique = "%PARAMETER%"
    sql_text = sql_text.replace("?", unique)
    for v in values:
        sql_text = sql_text.replace(unique, repr(v), 1)
    return sql_text


# search is case insensitive
def get_fidodata_by_addr(fido_addr):
    result = ''

    try:
        sql_text = 'SELECT fido_addr, fido_name \
            FROM fidonetlist\
            WHERE fido_addr = "{data}" \
            order by fido_addr LIMIT 1\
            COLLATE NOCASE'.format(data=fido_addr)

        cursor.execute(sql_text)
    except Exception as e:
        raise e

    if cursor:
        for row in cursor:
            data = row[0] + ", " + row[1]
            result = data

    return result


def add_New_User(fido_addr, fido_name):
    add_New_User_Query = "insert into fidonetlist\
                          (fido_addr, fido_name) values (?, ?)"

    try:
        cursor.execute(add_New_User_Query, (fido_addr, fido_name, ))
        connection.commit()
    except Exception as e:
        print(check_sql_string(add_New_User_Query, (fido_addr, fido_name, )))
        raise(e)

    return cursor.rowcount


version = '0.01'
# default script params
def_parms = dict(input_fn='PNT5011.parsed.TXT')

# getting script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Look at command-line args
parser = argparse.ArgumentParser(description='This script insert fidonet data at db.')

parser.add_argument('--input', '-i', type=str,
                    default='PNT5011.parsed.TXT',
                    help='Input file name. \
                    Default value is "PNT5011.parsed.TXT"')


args = parser.parse_args()

print('----   ---   start working   ----   ---')

os.chdir(script_dir)
copyfile(config.dbname, config.dbname + '.bak')

dbname = config.dbname
try:
    connection = sqlite3.connect(dbname, check_same_thread=False)
    cursor = connection.cursor()
except Exception as e:
    raise e

print('Parse file ', args.input)

added = 0
skipped = 0

with codecs.open(args.input, "r", "utf-8") as fido_file_in:
    for single_line in fido_file_in:
        single_line = single_line.rstrip()

        fidodata_list = single_line.split(',')
        check_res = get_fidodata_by_addr(fidodata_list[0])
        if check_res == '':
            add_New_User(fidodata_list[0], fidodata_list[1])
            added += 1
        else:
            skipped += 1

print('Added ', added)
print('Skipped ', skipped)
print('Done')
