
import collections
import string

from timeit import default_timer
from urllib.parse import urldefrag, urljoin, urlparse

import bs4
import requests

#------------------------------------------------------------------------------
def crawler(startpage, maxpages=100, singledomain=True):
    """Crawl the web starting from specified page.

    1st parameter = URL of starting page
    maxpages = maximum number of pages to crawl
    singledomain = whether to only crawl links within startpage's domain
    """

    pagequeue = collections.deque() # 即將被下載的頁面的queue
    pagequeue.append(startpage)
    crawled = [] # 已爬過的頁面
    domain = urlparse(startpage).netloc if singledomain else None

    pages = 0 # 至今成功爬取的頁面數
    failed = 0 # 失敗的頁面數

    sess = requests.session() # 初始化session
    while pages < maxpages and pagequeue:
        url = pagequeue.popleft() # 取得下一個代下載的頁面 (FIFO queue)

        # read the page
        try:
            response = sess.get(url)
        except (requests.exceptions.MissingSchema,
                requests.exceptions.InvalidSchema):
            print("*FAILED*:", url)
            failed += 1
            continue
        if not response.headers['content-type'].startswith('text/html'):
            continue # 非HTML的頁面不處理

        # 注意，我們在這裏建立 Beautiful Soup 物件
        # 並將它傳入子函式使用
        soup = bs4.BeautifulSoup(response.text, "html.parser")

        # 處理頁面
        crawled.append(url)
        pages += 1
        if pagehandler(url, response, soup):
            # 取得頁面中的所有連結，並放到crawler queue裏面
            links = getlinks(url, domain, soup)
            for link in links:
                if not url_in_list(link, crawled) and not url_in_list(link, pagequeue):
                    pagequeue.append(link)

    print('{0} pages crawled, {1} links failed.'.format(pages, failed))

#-------------------------------------------------------------------------------
def getcounts(words=None):
    """Convert a list of words into a dictionary of word/count pairs.
    Does not include words not deemed interesting.
    """

    # create a dictionary of key=word, value=count
    counts = collections.Counter(words)

    # save total word count before removing common words
    wordsused = len(counts)

    # remove common words from the dictionary
    shortwords = [word for word in counts if len(word) < 3] # no words <3 chars
    ignore = shortwords + \
        ['after', 'all', 'and', 'are', 'because', 'been', 'but', 'for', 'from',
         'has', 'have', 'her', 'more', 'not', 'now', 'our', 'than', 'that',
         'the', 'these', 'they', 'their', 'this', 'was', 'were', 'when', 'who',
         'will', 'with', 'year', 'hpv19slimfeature', 'div']
    for word in ignore:
        counts.pop(word, None)

    # remove words that contain no alpha letters
    tempcopy = [_ for _ in words]
    for word in tempcopy:
        if noalpha(word):
            counts.pop(word, None)

    return (counts, wordsused)

#------------------------------------------------------------------------------
def getlinks(pageurl, domain, soup):
    """Returns a list of links from from this page to be crawled.

    pageurl = URL of this page
    domain = domain being crawled (None to return links to *any* domain)
    soup = BeautifulSoup object for this page
    """

    # get target URLs for all links on the page
    links = [a.attrs.get('href') for a in soup.select('a[href]')]

    # remove fragment identifiers
    links = [urldefrag(link)[0] for link in links]

    # remove any empty strings
    links = [link for link in links if link]

    # if it's a relative link, change to absolute
    links = [link if bool(urlparse(link).netloc) else urljoin(pageurl, link) \
        for link in links]

    # if only crawing a single domain, remove links to other domains
    if domain:
        links = [link for link in links if samedomain(urlparse(link).netloc, domain)]

    return links

#-------------------------------------------------------------------------------
def getwords(rawtext):
    """Return a list of the words in a text string.
    """
    words = []
    cruft = ',./():;!"' + "<>'â{}" # characters to strip off ends of words
    for raw_word in rawtext.split():
        # remove whitespace before/after the word
        word = raw_word.strip(string.whitespace + cruft + '-').lower()

        # remove posessive 's at end of word
        if word[-2:] == "'s":
            word = word[:-2]

        if word: # if there's anything left, add it to the words list
            words.append(word)

    return words

#------------------------------------------------------------------------------
def pagehandler(pageurl, pageresponse, soup):
    """Function to be customized for processing of a single page.

    pageurl = URL of this page
    pageresponse = page content; response object from requests module
    soup = Beautiful Soup object created from pageresponse

    Return value = whether or not this page's links should be crawled.
    """
    print('Crawling:' + pageurl + ' ({0} bytes)'.format(len(pageresponse.text)))
    wordcount(soup) # display unique word counts
    return True

#------------------------------------------------------------------------------
def noalpha(word):
    """Determine whether a word contains no alpha characters.
    """
    for char in word:
        if char.isalpha():
            return False
    return True

#------------------------------------------------------------------------------
def samedomain(netloc1, netloc2):
    """Determine whether two netloc values are the same domain.

    This function does a "subdomain-insensitive" comparison. In other words ...

    samedomain('www.microsoft.com', 'microsoft.com') == True
    samedomain('google.com', 'www.google.com') == True
    samedomain('api.github.com', 'www.github.com') == True
    """
    domain1 = netloc1.lower()
    if '.' in domain1:
        domain1 = domain1.split('.')[-2] + '.' + domain1.split('.')[-1]

    domain2 = netloc2.lower()
    if '.' in domain2:
        domain2 = domain2.split('.')[-2] + '.' + domain2.split('.')[-1]

    return domain1 == domain2

#------------------------------------------------------------------------------
def url_in_list(url, listobj):
    """Determine whether a URL is in a list of URLs.

    This function checks whether the URL is contained in the list with either
    an http:// or https:// prefix. It is used to avoid crawling the same
    page separately as http and https.
    """
    http_version = url.replace('https://', 'http://')
    https_version = url.replace('http://', 'https://')
    return (http_version in listobj) or (https_version in listobj)

#------------------------------------------------------------------------------
def wordcount(soup):
    """Display word counts for a crawled page.

    pageresponse = page content; response object from requests module
    soup = Beautiful Soup object created from pageresponse

    This is an example of a page handler. Just creates a list of unique words on
    the page and displays the word counts.
    """
    rawtext = soup.get_text()
    print(rawtext)
    words = getwords(rawtext)
    counts, _ = getcounts(words)
    if counts.most_common(1)[0][1] < 10:
        print('This page does not have any words used more than 10 times.')
    else:
        print(counts.most_common(10))

#------------------------------------------------------------------------------
# if running standalone, crawl some Microsoft pages as a test
if __name__ == "__main__":
    START = default_timer()
    crawler('http://www.pingle.com.tw', maxpages=100, singledomain=True)
    END = default_timer()
    print('Elapsed time (seconds) = ' + str(END-START))
