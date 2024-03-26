# flake8: noqa: F401, F403
import abc
import argparse
import collections
import csv
import json
import multiprocessing as mp
import numpy as np
import os, sys, time, base64, io
import os.path as osp
import copy as cp
import pickle
import random as rd
import requests
import shutil
import string
import subprocess
import warnings
import pandas as pd
from collections import OrderedDict, defaultdict
from multiprocessing import Pool, current_process
from tqdm import tqdm
from PIL import Image
import uuid
from uuid import uuid4
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate

def d2df(D):
    return pd.DataFrame({x: [D[x]] for x in D})

def LMUDataRoot():
    if 'LMUData' in os.environ and osp.exists(os.environ['LMUData']):
        return os.environ['LMUData']
    home = osp.expanduser('~')
    root = osp.join(home, 'LMUData')
    os.makedirs(root, exist_ok=True)
    return root

def cn_string(s):
    import re
    if re.search(u'[\u4e00-\u9fff]', s):
        return True
    return False

def timestr(second=False, minute=False):
    s = datetime.now().strftime('%Y%m%d%H%M%S')[2:]
    if second:
        return s
    elif minute:
        return s[:-2]
    else:
        return s[:-4]
    
def num2uuid(num):
    rd.seed(num)
    return str(uuid.UUID(int=rd.getrandbits(128), version=4))

def randomuuid():
    seed = rd.randint(0, 2 ** 32 - 1)
    return num2uuid(seed)

def mrlines(fname, sp='\n'):
    f = open(fname).read().split(sp)
    while f != [] and f[-1] == '':
        f = f[:-1]
    return f

def mwlines(lines, fname):
    with open(fname, 'w') as fout:
        fout.write('\n'.join(lines))

def default_set(self, args, name, default):
    if hasattr(args, name):
        val = getattr(args, name)
        setattr(self, name, val)
    else:
        setattr(self, name, default)

def dict_merge(dct, merge_dct):
    for k, _ in merge_dct.items():
        if (k in dct and isinstance(dct[k], dict) and isinstance(merge_dct[k], dict)):  #noqa
            dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]

def youtube_dl(idx):
    cmd = f'youtube-dl -f best -f mp4 "{idx}"  -o {idx}.mp4'
    os.system(cmd)

def run_command(cmd):
    if isinstance(cmd, str):
        cmd = cmd.split()
    return subprocess.check_output(cmd)

def ls(dirname='.', match='', mode='all', level=1):
    if dirname == '.':
        ans = os.listdir(dirname)
    else:
        ans = [osp.join(dirname, x) for x in os.listdir(dirname)]
    assert mode in ['all', 'dir', 'file']
    assert level >= 1 and isinstance(level, int)
    if level == 1:
        ans = [x for x in ans if match in x]
        if mode == 'dir':
            ans = [x for x in ans if osp.isdir(x)]
        elif mode == 'file':
            ans = [x for x in ans if not osp.isdir(x)]
    else:
        ans = [x for x in ans if osp.isdir(x)]
        res = []
        for d in ans:
            res.extend(ls(d, match=match, mode=mode, level=level-1))
        ans = res
    return ans

def intop(pred, label, n):
    pred = [np.argsort(x)[-n:] for x in pred]
    hit = [(l in p) for l, p in zip(label, pred)]
    return hit

def topk(score, label, k=1):
    return np.mean(intop(score, label, k)) if isinstance(k, int) else [topk(score, label, kk) for kk in k]

def download_file(url, filename=None):
    if filename is None:
        filename = url.split('/')[-1]
    response = requests.get(url)
    open(filename, 'wb').write(response.content)

def fnp(model, input=None):
    from fvcore.nn import FlopCountAnalysis, parameter_count
    params = parameter_count(model)['']
    print('Parameter Size: {:.4f} M'.format(params / 1024 / 1024))
    if input is not None:
        flops = FlopCountAnalysis(model, input).total()
        print('FLOPs: {:.4f} G'.format(flops / 1024 / 1024 / 1024))
        return params, flops
    return params, None

def proxy_set(s):
    import os
    for key in ['http_proxy', 'HTTP_PROXY', 'https_proxy', 'HTTPS_PROXY']:
        os.environ[key] = s

# LOAD & DUMP
def dump(data, f, **kwargs):
    def dump_pkl(data, pth, **kwargs):
        pickle.dump(data, open(pth, 'wb'))

    def dump_json(data, pth, **kwargs):
        json.dump(data, open(pth, 'w'), indent=4, ensure_ascii=False)

    def dump_jsonl(data, f, **kwargs):
        lines = [json.dumps(x, ensure_ascii=False) for x in data]
        with open(f, 'w', encoding='utf8') as fout:
            fout.write('\n'.join(lines))

    def dump_xlsx(data, f, **kwargs):
        data.to_excel(f, index=False)

    def dump_csv(data, f, quoting=csv.QUOTE_MINIMAL):
        data.to_csv(f, index=False, encoding='utf-8', quoting=quoting)

    def dump_tsv(data, f, quoting=csv.QUOTE_MINIMAL):
        data.to_csv(f, sep='\t', index=False, encoding='utf-8', quoting=quoting)

    handlers = dict(pkl=dump_pkl, json=dump_json, jsonl=dump_jsonl, xlsx=dump_xlsx, csv=dump_csv, tsv=dump_tsv)
    suffix = f.split('.')[-1]
    return handlers[suffix](data, f, **kwargs)

import portalocker
def safe_dump(data, f, **kwargs):
    with portalocker.Lock(f, timeout=5) as fh:
        dump(data, f, **kwargs)
        fh.flush()
        os.fsync(fh.fileno())

def load(f):
    def load_pkl(pth):
        return pickle.load(open(pth, 'rb'))

    def load_json(pth):
        return json.load(open(pth, 'r', encoding='utf-8'))

    def load_jsonl(f):
        lines = open(f, encoding='utf-8').readlines()
        lines = [x.strip() for x in lines]
        if lines[-1] == '':
            lines = lines[:-1]
        data = [json.loads(x) for x in lines]
        return data

    def load_xlsx(f):
        return pd.read_excel(f)

    def load_csv(f):
        return pd.read_csv(f)

    def load_tsv(f):
        return pd.read_csv(f, sep='\t')

    handlers = dict(pkl=load_pkl, json=load_json, jsonl=load_jsonl, xlsx=load_xlsx, csv=load_csv, tsv=load_tsv)
    suffix = f.split('.')[-1]
    return handlers[suffix](f) 