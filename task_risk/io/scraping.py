# pull the data using web scraping
# ref: https://realpython.com/python-web-scraping-practical-introduction/

from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import html
import urllib



def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content.decode()
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)


def get_from_pmc(url, outfile):
    '''
    url = 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5493079/'
    '''
    raw_html = simple_get(url)
    soup = BeautifulSoup(raw_html, 'html.parser')
    with open(outfile, 'w+') as f:
        for p in soup.select('p[id^=Par]'):
            f.write(p.text)
    print(f'finished writing {url} to {outfile}')


def get_from_doi(url, outfile):
    '''
    url = 'https://doi.org/10.1378/chest.14-2129'
    '''
    raw_html = simple_get(url)
    soup = BeautifulSoup(raw_html, 'html.parser')
    redirect = soup.find_all(id="redirectURL")[0]["value"]
    redirect = urllib.parse.unquote(redirect)
    raw_html = simple_get(redirect)
    soup = BeautifulSoup(raw_html, 'html.parser')
    with open(outfile, 'w+') as f:
        for p in soup.find_all('div.pagefullText'):
            f.write(p.text)
    print(f'finished writing {url} to {outfile}')
