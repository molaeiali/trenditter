from __future__ import unicode_literals
from hazm import *
from nltk.chunk import tree2conlltags

def normalize(str):
    if len(str) == 0:
        return str
    if str[-1] is ' ':
        return str[:-1]
    return str

def tree2list(tree):
    str, tag = '', ''
    ret = []
    for item in tree2conlltags(tree):
        if item[2][0] in {'B', 'O'} and tag:
            ret.append((normalize(str), tag))
            tag = ''
            str = ''

        if item[2][0] == 'B':
            tag = item[2].split('-')[1]
            str += ''
        str += item[0] +' '

    if tag:
        ret.append((normalize(str), tag))

    return ret
