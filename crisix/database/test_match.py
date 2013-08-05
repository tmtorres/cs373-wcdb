import xml.etree.ElementTree as ET
from xml.etree.ElementTree import tostring, fromstring
from xml.etree.ElementTree import ElementTree
from substr import str_match

old = fromstring('<old><li>World Wide</li><li>New York</li></old>')
new = fromstring('<new><li>Worldwide</li><li>London</li></new>')

print tostring(str_match(new, old))

old = fromstring('<old><li>United States of America</li></old>')
new = fromstring('<new><li>United States of Mexico</li></new>')

print tostring(str_match(new, old))

old = fromstring('<old><li>Barack Obama</li></old>')
new = fromstring('<new><li>Michelle Obama</li></new>')

print tostring(str_match(new, old))

old = fromstring('<old><li>Barack Obama.</li></old>')
new = fromstring('<new><li>Barack Obama</li></new>')

print tostring(str_match(new, old))

old = fromstring('<old><li>Barack Obama and Michelle Obama live in America.</li></old>')
new = fromstring('<new><li>Barack Obama and Michelle Obama cohabit in America.</li></new>')

print tostring(str_match(new, old))

old = fromstring('<old><li>Barack Obama and Michelle Obama live in America.</li></old>')
new = fromstring('<new><li>Barack Obama and Michelle Obama play in France.</li></new>')

print tostring(str_match(new, old))
