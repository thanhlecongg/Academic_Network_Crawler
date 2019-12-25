# Created by Thanh C. Le at 2019-12-22
import hashlib
import pprint
import random
import re
import time
import scholarly

import arrow
import bibtexparser
import requests
from bs4 import BeautifulSoup

_GOOGLEID = hashlib.md5(str(random.random()).encode('utf-8')).hexdigest()[:16]
_COOKIES = {'GSP': 'ID={0}:CF=4'.format(_GOOGLEID)}
_HEADERS = {
    'accept-language': 'en-US,en',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/41.0.2272.76 Chrome/41.0.2272.76 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml'
    }
_HOST = 'https://scholar.google.com'
_AUTHSEARCH = '/citations?view_op=search_authors&hl=en&mauthors={0}'
_CITATIONAUTH = '/citations?user={0}&hl=en'
_CITATIONPUB = '/citations?view_op=view_citation&citation_for_view={0}'
_KEYWORDSEARCH = '/citations?view_op=search_authors&hl=en&mauthors=label:{0}'
_PUBSEARCH = '/scholar?q={0}'
_SCHOLARPUB = '/scholar?oi=bibs&hl=en&cites={0}'

_CITATIONAUTHRE = r'user=([\w-]*)'
_CITATIONPUBRE = r'citation_for_view=([\w-]*:[\w-]*)'
_SCHOLARCITERE = r'gs_ocit\(event,\'([\w-]*)\''
_SCHOLARPUBRE = r'cites=([\w-]*)'
_EMAILAUTHORRE = r'Verified email at '

_SESSION = requests.Session()
_PAGESIZE = 100


class Publication(object):
    """Returns an object for a single publication"""

    def __init__(self, __data):
        self.bib = dict()
        databox = __data.find('div', class_='gs_ri')
        title = databox.find('h3', class_='gs_rt')
        if title.find('span', class_='gs_ctu'):  # A citation
            title.span.extract()
        elif title.find('span', class_='gs_ctc'):  # A book or PDF
            title.span.extract()
        self.bib['title'] = title.text.strip()
        if title.find('a'):
            self.bib['url'] = title.find('a')['href']
        authorinfo = databox.find('div', class_='gs_a')
        self.bib['author'] = ' and '.join([i.strip() for i in authorinfo.text.split(' - ')[0].split(',')])
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
        if __data.find('div', class_='gs_ggs gs_fl'):
            self.bib['eprint'] = __data.find('div', class_='gs_ggs gs_fl').a['href']

    def get_citedby(self):
        pass

    def __str__(self):
        return pprint.pformat(self.__dict__)

def get_page(pagerequest):
    """Return the data for a page on scholar.google.com"""
    resp = _SESSION.get(pagerequest, headers=_HEADERS, cookies=_COOKIES)
    if resp.status_code == 200:
        return resp.text
    if resp.status_code == 503:
        raise Exception('Error: {0} {1}'.format(resp.status_code, resp.reason))
    else:
        raise Exception('Error: {0} {1}'.format(resp.status_code, resp.reason))


def get_soup(pagerequest):
    """Return the BeautifulSoup for a page on scholar.google.com"""
    html = get_page(pagerequest)
    html = html.replace(u'\xa0', u' ')
    return BeautifulSoup(html, 'html.parser')

def search_scholar_soup(soup):
    """Generator that returns Publication objects from the search page"""
    while True:
        for row in soup.find_all('div', 'gs_or'):
            yield Publication(row, 'scholar')
        if soup.find(class_='gs_ico gs_ico_nav_next'):
            url = soup.find(class_='gs_ico gs_ico_nav_next').parent['href']
            soup = get_soup(_HOST+url)
        else:
            break

def search_publication_bytitle(title):
    """Search by scholar query and return a generator of Publication objects"""
    url = _PUBSEARCH.format(requests.utils.quote(title))
    soup = get_soup(_HOST + url)
    return search_scholar_soup(soup)

if __name__ == '__main__':
    print(next(search_publication_bytitle("graph2vec: Learning distributed representations of graphs")))