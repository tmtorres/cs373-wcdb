import xml.etree.ElementTree as ET
from xml.etree.ElementTree import tostring, fromstring
from xml.etree.ElementTree import ElementTree

def long_substr(data):
    substr = ''
    if len(data) > 1 and len(data[0]) > 0:
        for i in range(len(data[0])):
            for j in range(len(data[0])-i+1):
                if j > len(substr) and all(data[0][i:i+j] in x for x in data):
                    substr = data[0][i:i+j]
    return substr

'''
def relevance_sort(query_string, search_fields, query_set):
    result_set = []
    for entry in query_set:
        substr = [long_substr([getattr(entry, field).lower(), query_string.lower()]) for field in search_fields]
        match = float(max([len(s) for s in substr])) / len(query_string)
        result_set += [(match, entry)]
    return zip(*sorted(result_set, key=lambda x: x[0], reverse=True))[1] if len(result_set) else result_set
'''

def str_match(new, old):
    '''
    new is an ElementTree of new content to be added
    old is an ElementTree of info in the database
    '''
    for new_li in new:
        substr = [(long_substr([new_li.text.strip(), old_li.text.strip()]), old_li) for old_li in old]
        match = sorted(substr, key=lambda x: len(x[0]), reverse=True)[0]
        diff_str = [new_li.text.replace(match[0], '', 1).strip(), match[1].text.replace(match[0], '', 1).strip()]
        if not len(diff_str[0]) or not len(diff_str[1]):
            match[1].text = new_li.text
        elif (float(len(long_substr(diff_str))) / len(diff_str[1])) > 0.4:
            match[1].text = new_li.text
        else:
            ET.SubElement(old, 'li').text = new_li.text
    return old
