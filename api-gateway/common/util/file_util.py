# edit at 2024-04-01
# cp /Users/kimmyounghoon/Works/mkay/common/api-gateway/common/util/* ./api-gateway/common/util/

import io, sys, time, os, glob, pprint, json, re, shutil, ntpath, csv

import os

def line_count(file, encoding='utf-8'):
    with open(file, 'r', encoding=encoding) as f:
        return sum(1 for _ in f)

def remove_file(file):
    print(f'remove_file {file}')
    if os.path.exists(file):
        os.remove(file)

def remove_geo_files(filename_wo_ext):
    remove_file(filename_wo_ext + '.shp')
    remove_file(filename_wo_ext + '.shx')
    remove_file(filename_wo_ext + '.dbf')
    remove_file(filename_wo_ext + '.fix')

def file_split(file):
    s = file.split('.')
    name = '.'.join(s[:-1])  # get directory name
    return name

def getsheets(inputfile, fileformat='csv'):
    import pandas as pd
    name = file_split(inputfile)
    try:
        os.makedirs(name)
    except:
        pass

    df1 = pd.ExcelFile(inputfile)
    for x in df1.sheet_names:
        print(x + '.' + fileformat, 'Done!')
        df2 = pd.read_excel(inputfile, sheet_name=x)
        filename = os.path.join(name, x + '.' + fileformat)
        df2.to_csv(filename, index=False)
    print('\nAll Done!')