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

def li_match(new, old):
    '''
    new is an ElementTree of new content to be added
    old is an ElementTree of info in the database
    '''
    if not len(list(old)):
        return ''.join([tostring(li).strip() for li in new])

    for new_li in new:
        subseq = [(lcs(new_li.text.strip().lower(), old_li.text.strip().lower()), old_li) for old_li in old]
        match = max(subseq, key=lambda x: len(x[0]))
        while(float(len(match[0])) / len(match[1].text)) > 0.4:
            old.remove(match[1])
            subseq = [(lcs(new_li.text.strip().lower(), old_li.text.strip().lower()), old_li) for old_li in old]
            try:
                match = max(subseq, key=lambda x: len(x[0]))
            except ValueError:
                break
        ET.SubElement(old, 'li').text = new_li.text
    return ''.join([tostring(li).strip() for li in old])

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
            
