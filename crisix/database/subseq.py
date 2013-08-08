# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import tostring, fromstring
from xml.etree.ElementTree import ElementTree
import nltk, os
from django.conf import settings

def lcs(a, b):
    lengths = [[0 for j in range(len(b)+1)] for i in range(len(a)+1)]
    # row 0 and column 0 are initialized to 0 already
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            if x == y:
                lengths[i+1][j+1] = lengths[i][j] + 1
            else:
                lengths[i+1][j+1] = \
                    max(lengths[i+1][j], lengths[i][j+1])
    # read the substring out from the matrix
    result = ""
    x, y = len(a), len(b)
    while x != 0 and y != 0:
        if lengths[x][y] == lengths[x-1][y]:
            x -= 1
        elif lengths[x][y] == lengths[x][y-1]:
            y -= 1
        else:
            assert a[x-1] == b[y-1]
            result = a[x-1] + result
            x -= 1
            y -= 1
    return result

from crisix.views import convert_li
def li_match(new, old):
    '''
    new is an ElementTree of new content to be added
    old is an ElementTree of info in the database
    '''
    if not len(list(old)):
        return ''.join([tostring(li).strip() for li in new])

    new_href = dict([(li.attrib.get('href'), li) for li in new if li.attrib.get('href') is not None])
    new_text = convert_li(''.join([tostring(li).strip() for li in new if li not in new_href.values()]))
    old_href = dict([(li.attrib.get('href'), li) for li in old if li.attrib.get('href') is not None])
    old_text = convert_li(''.join([tostring(li).strip() for li in old if li not in old_href.values()]))
    merged_text = seq_match(old_text, new_text)
    merged_href = dict(old_href.items() + new_href.items())
    print merged_text
    print merged_href
    return '<li>' + merged_text + '</li>' + ''.join([tostring(li).strip() for li in merged_href.values()])

def seq_match(new, old):
    '''
    new is a string of new content to be added
    old is a string of info in the database
    '''
    if not len(old):
        return new

    tokenizer = nltk.data.load('file:' + os.path.join(settings.BASE_DIR, 'nltk_data/tokenizers/punkt/english.pickle'))
    new = tokenizer.tokenize(new)
    old = tokenizer.tokenize(old)

    for line in new:
        subseq = [(lcs(line.strip().lower(), old[i].strip().lower()), i) for i in range(0, len(old))]
        match = max(subseq, key=lambda x: len(x[0]))
        if (float(len(match[0])) / len(old[match[1]])) > 0.4:
            old[match[1]] = line
        else:
            old += [line]
    return ' '.join(old)
            
