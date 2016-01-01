import re

from bs4 import BeautifulSoup

def get_value_for_name(name, unicode_text):
    soup = BeautifulSoup(unicode_text, 'html.parser')
    t = soup.find(attrs={'name': name})
    return t.attrs.get('value')