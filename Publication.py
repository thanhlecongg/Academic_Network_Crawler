# Created by Thanh C. Le at 2020-01-06
import pprint
import re

import numpy as np
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
from tqdm import tqdm

from Author import Author

_SCHOLARPUBRE = r'cites=([\w-]*)'

class Publication(object):
    """Returns an object for a single publication"""

    def __init__(self, databox):
        self.bib = dict()
        title = databox.find('h3', class_='gs_rt')
        if title.find('span', class_='gs_ctu'):
            title.span.extract()
        elif title.find('span', class_='gs_ctc'):
            title.span.extract()
        self.bib['title'] = title.text.strip()
        if title.find('a'):
            self.bib['url'] = title.find('a')['href']
            self.id = title.find('a')['id']
        authorinfo = databox.find('div', class_='gs_a').find_all('a')
        self.authors = []
        for authorlink in authorinfo:
            author = Author(authorlink.text,authorlink['href'])
            self.authors.append(author)
        if databox.find('div', class_='gs_rs'):
            self.bib['abstract'] = databox.find('div', class_='gs_rs').text
            if self.bib['abstract'][0:8].lower() == 'abstract':
                self.bib['abstract'] = self.bib['abstract'][9:].strip()
        lowerlinks = databox.find('div', class_='gs_fl').find_all('a')
        for link in lowerlinks:
            if 'Import into BibTeX' in link.text:
                self.url_scholarbib = link['href']
            if 'Cited by' in link.text:
                self.citedby = int(re.findall(r'\d+', link.text)[0])
                self.id_scholarcitedby = re.findall(_SCHOLARPUBRE, link['href'])[0]

    def get_citedby(self):
        pass

    def __str__(self):
        return pprint.pformat(self.__dict__)