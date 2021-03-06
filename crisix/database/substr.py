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

def str_match(new, old):
    '''
    new is an ElementTree of new content to be added
    old is an ElementTree of info in the database
    '''
    if len(list(old)) == 0:
        return new

    for new_li in new:
        substr = [(long_substr([new_li.text.strip().lower(), old_li.text.strip().lower()]), old_li) for old_li in old]
        match = max(substr, key=lambda x: len(x[0]))
        diff_str = [new_li.text.lower().replace(match[0], '', 1).strip(), match[1].text.lower().replace(match[0], '', 1).strip()]
        if not (len(diff_str[0]) and len(diff_str[1])) or (float(len(long_substr(diff_str))) / len(diff_str[1])) > 0.4:
            match[1].text = new_li.text
        else:
            ET.SubElement(old, 'li').text = new_li.text
    return old
