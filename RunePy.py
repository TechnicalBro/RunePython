import urllib2
import urllib
import re
import os
import sys
from time import strftime, localtime
from texttable import Texttable
from termcolor import colored
from bs4 import BeautifulSoup

def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""

def clear_console():
    os.system("cls" if os.name == "nt" else "clear")

def local_time():
    return strftime("%I:%M:%S %d-%m-%Y", localtime())


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


class AdventurerLogEntry:

    def __init__(self, status, description, date):
        self.status = status
        self.date = date
        self.description = description

class AdventuresLog:
    __LOG_BASE_URL__ = "http://services.runescape.com/m=adventurers-log/rssfeed?searchName="

    def __init__(self, username):
        #Store our username
        self.username = username
        #Store our adventurer's log link
        self.adventurer_log_link = self.__LOG_BASE_URL__ + urllib.quote_plus(username)
        self.log_items = self.__parse_adventurer_log__()

    def __parse_adventurer_log__(self):
        feed = urllib2.urlopen(self.adventurer_log_link)
        log_html = BeautifulSoup(feed.read(), 'xml')
        entries = []
        for logitem in log_html.findAll('item'):
            logitem.hidden = True
            log_entry = AdventurerLogEntry(unicode(logitem.title.string), unicode(logitem.description.string), unicode(logitem.pubDate.string))
            entries.append(log_entry)
        return entries

    def print_log(self):
        table = Texttable(140)
        table.set_cols_dtype(['t', 't', 't'])
        table.set_cols_align(['l', 'l', 'l'])
        table.add_row(['Action','Description','Date'])
        for logitem in self.log_items:
            print "Status = " + logitem.status + " Desc = " + logitem.description + " date = " + logitem.date
            table.add_row([logitem.status, logitem.description, logitem.date])
        print table.draw()


def item_search():
    while True:
        itemsearch = raw_input("Please enter an item name: ")
        if itemsearch:
            geItem = GrandExhangeSearch(itemsearch)
            while True:
                clear_console()
                viewitems = raw_input("There were " + str(geItem.search_results_count) + " results to your search, view them? [y/n]: ").lower()
                if viewitems:
                    if viewitems == "y" or viewitems == "yes":
                        geItem.view_search_results()
                        break
                    elif viewitems == "n" or viewitems == "no":
                        break
                else:
                    clear_console()
                    print "Invalid option, please try again."
        else:
            break

def adventurer_log():
    while True:
        username = raw_input("Enter the username you wish to view, or enter 'exit' to return to the main menu: ")
        if username:
            if username.lower() == "exit":
                break
            else:
                adventurerlog = AdventuresLog(username)
                adventurerlog.print_log()
                raw_input("Press any key to continue...")
                clear_console()
        else:
            print colored("You didn't enter a username... Please try again.", "red")


def exit_prompt():
    print "Thank you for using RunePy. Press any key to exit..."
    raw_input("")
    sys.exit(0)

while True:
    print "Welcome to " + colored("RunePy", "green") + "."
    print "[1] Grand Exchange Search"
    print "[2] Adventurer Log Viewer"
    print "[0] " + colored("Exit", "yellow")
    user_option = raw_input("Please enter the option number: ")
    if user_option:
        if user_option == "0":
            exit_prompt()
        elif user_option == "1":
            item_search()
        elif user_option == "2":
            adventurer_log()
        else:
            print "You've not selected an option... Please try again"
            clear_console()
    else:
        print "You've not selected an option... Please try again"
        clear_console()
