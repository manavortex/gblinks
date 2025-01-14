# -*- coding: utf-8 -*-

import fnmatch
import markdown
import os
import re
import sys

from urllib.parse import urlparse

from importlib import reload
from lxml import html


# import urlparse python 2/3
if sys.version[0] == '2':
	from urlparse import urlparse
else:
	from urllib.parse import urlparse	

# if python 2, reload sys with encoding
if sys.version[0] == '2':
    reload(sys)
    sys.setdefaultencoding("utf-8")


def is_url(url):
    return urlparse(url).scheme != ''

def get_link_dict(file, link_text, link_url, link_path):
     data = {}
     data['file'] = os.path.normpath(file)
     data['link_text'] = link_text
     data['link_url'] = link_url
     data['link_path'] = os.path.normpath(link_path)

     return data;


class Gblinks:

    def __init__(self, path):
        if not os.path.isdir(path):
            raise ValueError('The given path is not valid')

        self.__mdfiles = self._get_markdown_files(path)

        if not self.__mdfiles:
            raise ValueError('The given path does not contain MarkDown files')

    def _files_iterator(self, path):
        for root, dirs, files in os.walk(path):
            for file in fnmatch.filter(files, '*.md'):
                yield root, file

    def _get_markdown_files(self, path):
        return list(self._files_iterator(path))

    def _link_iterator(self, markdown_file):
        if os.stat(markdown_file).st_size != 0:
            with open(markdown_file, 'r', encoding='utf-8') as file:
                data = file.read()

                doc = html.fromstring(markdown.markdown(data))
                for link in doc.xpath('//a'):
                    href = link.get('href')

                    if href and not bool(re.search('{{.*}}', href)):
                        yield link.text, href

    def check_broken_links(self):
        return self.get_links(only_broken=True, only_local=True)

    def get_links(self, only_broken=False, only_local=False):
        links = []

        for path, file in self.__mdfiles:
            markdown_file = os.path.join(path, file)
            for link_text, link_url in self._link_iterator(markdown_file):
                if (not only_local or not is_url(link_url)) and link_text is not None:
                    link_path = os.path.join(path, link_url.split('#')[0])
                    if os.path.isdir(link_path):
                        link_path = os.path.join(link_path, 'README.md')
                    if not only_broken or not os.path.exists(link_path):
                        links.append(get_link_dict(markdown_file, link_text, link_url, link_path))

        return links
