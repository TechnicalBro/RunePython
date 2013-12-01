import urllib2
import urllib
import re
from texttable import Texttable
from termcolor import colored

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
    __BASE_URL__ = "http://www.tip.it/runescape/grand-exchange-centre/search?itemsearch="

    #Dataset of start and end search tags for our amount of results
    __RESULTS_TAG__ = ['<p id="num_results">', '</p>']

    #Results Amount Tag
    __RESULT_AMOUNT_TAG__ = ['<span>', '</span>']

    #Dataset of start and end search tags for our table entries / item entires
    __TABLE_TAG__ = ['<table id="gec_search_results"', '</table>']

    #Regex compile to match against all table rows in the HTML
    __TABLE_ENTRY_REGEX__ = '<tr>.*?</tr>'

    #Dataset to parse for the items id
    __ITEM_ID_TAG__ = ['data-itemid="', '"']

    #Dataset to parse to get the items name
    __ITEM_NAME_TAG__ = ['href="http://www.tip.it/runescape//grand-exchange-centre/view/[ITEMID]">', '</a>']

    #Dataset to parse to get the items price
    __ITEM_PRICE_TAG__ = ['[ITEMNAME]</a></td><td>', '</td><td>']

    #Dataset to parse to get the items change
    __ITEM_CHANGE_TAG__ = ['[ITEMPRICE]</td><td>', '</td><td><a href=']

    #Class initialization
    def __init__(self, search_item):
        #Define our search item
        self.search_item = search_item
        #Define our search URL
        self.search_url = self.__BASE_URL__ + urllib.quote_plus(self.search_item)
        pagedata = self.__getpagedata__()
        self.search_results_count = self.__get_search_amount__(pagedata)
        self.search_results = self.__get_search_entries__(pagedata)

    def __get_search_amount__(self, pagedata):
        #Find the data to parse to find our amount of results
        searchresults = find_between(pagedata, self.__RESULTS_TAG__[0], self.__RESULTS_TAG__[1])
        #Find the amount of results and format the commas in it
        searchamount = find_between(searchresults, self.__RESULT_AMOUNT_TAG__[0], self.__RESULT_AMOUNT_TAG__[1])\
            .replace(",", "")
        return int(searchamount)

    def __get_search_entries__(self, pagedata):
        #Create our list to return
        entries = []
        #Get the data for our table by parsing the strings between
        table_data = find_between(pagedata, self.__TABLE_TAG__[0], self.__TABLE_TAG__[1])
        #Match against table data to get all item entires
        re_entries = re.compile(self.__TABLE_ENTRY_REGEX__, re.IGNORECASE | re.DOTALL)
        #Loop through the matches to create our items
        for match in re_entries.findall(table_data):
            #Find the item ID
            item_id = find_between(match, self.__ITEM_ID_TAG__[0], self.__ITEM_ID_TAG__[1])
            #Find the item name
            item_name = find_between(match, self.__ITEM_NAME_TAG__[0].replace("[ITEMID]", item_id), self.__ITEM_NAME_TAG__[1])
            #Find the item price
            item_price = find_between(match, self.__ITEM_PRICE_TAG__[0].replace("[ITEMNAME]", item_name), self.__ITEM_PRICE_TAG__[1])
            #Find the items change today
            item_change = find_between(match, self.__ITEM_CHANGE_TAG__[0].replace("[ITEMPRICE]", item_price), self.__ITEM_CHANGE_TAG__[1])
            #Append it to the data to return
            entries.append(SearchItem(item_name, item_price, item_change))
        return entries

    def __getpagedata__(self):
        response = urllib2.urlopen(self.search_url)
        return response.read()

    def view_search_results(self):
        table = Texttable(120)

        table.set_cols_dtype(['t','t','t'])
        table.set_cols_align(['c','c','c'])
        table.add_row(["Item Name","Item Price", "Daily Change"])
        for item in self.search_results:
            itemchange_color = ""
            if "+" in item.itemchange:
                itemchange_color = "green"
            elif "-" in item.itemchange:
                itemchange_color = "red"
            else:
                itemchange_color = "yellow"
            table.add_row([item.itemname, item.itemprice, colored(item.itemchange,itemchange_color)])
        print table.draw()

while True:
    itemsearch = raw_input("Please enter an item name: ")
    if itemsearch:
        geItem = GrandExhangeSearch(itemsearch)
        while True:
            viewitems = raw_input("There were " + str(geItem.search_results_count) + " results to your search, view them? [y/n]: ").lower()
            if viewitems:
                if viewitems == "y" or viewitems == "yes":
                    geItem.view_search_results()
                    break
                elif viewitems == "n" or viewitems == "no":
                    break
            else:
                print "Invalid option, please try again."
    else:
        break
