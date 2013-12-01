import urllib2
import urllib
import re

def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""


class SearchItem:
    def __init__(self, itemname = "", itemprice = "", itemchange = ""):
        self.itemname = itemname
        self.itemprice = itemprice
        self.itemchange = itemchange

    def get_item_name(self):
        return self.itemname

    def get_item_price(self):
        return self.itemprice

    def get_item_change(self):
        return self.itemchange

class GrandExhangeSearch:
    #Base url for all the item searches we'll do
    _BASE_URL = "http://www.tip.it/runescape/grand-exchange-centre/search?itemsearch="
    #Dataset of start and end search tags for our amount of results
    _RESULTS_TAG = ['<p id="num_results">', '</p>']
    #Results Amount Tag
    _RESULT_AMOUNT_TAG = ['<span>', '</span>']
    #Dataset of start and end search tags for our table entries / item entires
    _TABLE_TAG = ['<table id="gec_search_results"', '</table>']

    _TABLE_ENTRY_REGEX = '<tr>.*?</tr>'

    search_results = []

    search_results_count = 0

    #Class initialization
    def __init__(self, item):
        #Define our search item
        self.item = item
        #Define our search URL
        self.itemurl = self._BASE_URL + urllib.quote_plus(self.item)
        print "Created a new search for " + item + " with url + " + self.itemurl
        pagedata = self._getpagedata()
        self.search_results_count = self._get_search_amount(pagedata)
        print "There are " + str(self.search_results_count) + " search results"
        self.search_results = self._get_search_entries(pagedata)
        for sr in self.search_results:
            print "Item " + sr.itemname + " has a price of " + sr.itemprice + " with a change of " + sr.itemchange

    def _get_search_amount(self, pagedata):
        #Find the data to parse to find our amount of results
        searchresults = find_between(pagedata, self._RESULTS_TAG[0], self._RESULTS_TAG[1])
        #Find the amount of results and format the commas in it
        searchamount = find_between(searchresults, self._RESULT_AMOUNT_TAG[0], self._RESULT_AMOUNT_TAG[1])\
            .replace(",", "")
        return int(searchamount)

    def _get_search_entries(self, pagedata):
        entries = []
        table_data = find_between(pagedata, self._TABLE_TAG[0], self._TABLE_TAG[1])
        re_entries = re.compile(self._TABLE_ENTRY_REGEX, re.IGNORECASE | re.DOTALL)
        for match in re_entries.findall(table_data):
            item_id = find_between(match,'data-itemid="','"')
            datamatch = '.*?(\w+).*?</td><td>(\S+)</td><td>'
            print "Found item id for " + self.item + " to be " + item_id
            item_regex = re.compile(datamatch)
            data = item_regex.search(find_between(match, 'data-itemid="' + item_id + '"', '<a href=').replace(",", ""))
            entries.append(SearchItem(data.group(0), data.group(1), data.group(2)))
        return entries

    def _getpagedata(self):
        response = urllib2.urlopen(self.itemurl)
        return response.read()

while True:
    itemsearch = raw_input("Please enter an item name: ")
    if itemsearch:
        geItem = GrandExhangeSearch(itemsearch)


