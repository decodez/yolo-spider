import re
from urllib.parse import urljoin, urlsplit, SplitResult
import requests
from bs4 import BeautifulSoup
import csv
import sys

class RecursiveScraper:

    sys.setrecursionlimit(10000);
 
    def __init__(self, url):
 
        self.domain = urlsplit(url).netloc
        self.mainurl = url
        self.urls = set()

    def preprocess_url(self, referrer, url):
        ''' Clean and filter URLs before scraping.
        '''
        if not url:
            return None

        fields = urlsplit(urljoin(referrer, url))._asdict() # convert to absolute URLs and split
        fields['path'] = re.sub(r'/$', '', fields['path']) # remove trailing /
        fields['fragment'] = '' # remove targets within a page
        fields = SplitResult(**fields)
        if fields.netloc == self.domain:
            # Scrape pages of current domain only
            if fields.scheme == 'http':
                httpurl = cleanurl = fields.geturl()
                httpsurl = httpurl.replace('http:', 'https:', 1)
            else:
                httpsurl = cleanurl = fields.geturl()
                httpurl = httpsurl.replace('https:', 'http:', 1)
            if httpurl not in self.urls and httpsurl not in self.urls:
                # Return URL only if it's not already in list
                return cleanurl

        return None

    def scrape(self, url=None):
        ''' Scrape the URL and its outward links in a depth-first order.
            If URL argument is None, start from main page.
        '''
        if url is None:
            url = self.mainurl

        

        head = requests.head(url)
    
        contentType = head.headers['Content-Type']

        if 'text/html' in contentType:
            files = re.search('(.doc|.docx|.pdf|.png|.jpg|.jpeg|.xls)$', url)
            if (files == None):
                print("Scraping {:s} ...".format(url))  
                response = requests.get(url)
                self.urls.add(url)
                soup = BeautifulSoup(response.content, 'html5lib')
                for link in soup.findAll("a"):
                    childurl = self.preprocess_url(url, link.get("href"))
                    if childurl:
                        if "output=printable" not in childurl:
                            self.scrape(childurl)
            else: 
                print("Skipping {:s} ...".format(url))
        else:
          print("Skipping {:s} ...".format(url))  


if __name__ == '__main__':
    rscraper = RecursiveScraper("https://www.olive.moe.edu.sg/")
    rscraper.scrape()
    csvFile = open('olive.csv', 'w+', newline='')
    try:
      writer = csv.writer(csvFile)
      writer.writerow(('number','url'))

      for url in rscraper.urls:
        writer.writerow(('',url))
    finally:
      csvFile.close()

