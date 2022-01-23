from bs4 import BeautifulSoup
import cloudscraper
import re
import os
import csv
from tabulate import tabulate
from typing import List
import itertools
from datetime import datetime, timedelta
import time
import logging
logging.basicConfig(level=logging.INFO)

MAX_ATTEMPTS = 10
FRESHNESS_THRESHOLD = 3
SEEN_FILEPATH = os.path.dirname(os.path.abspath(__file__)) + '/seen.csv'
TODAY = datetime.today()

class GuruScraper():
    def __init__(self, meta_dict, location, minprice=3.1e6, maxprice=5.3e6, freshness=3, ignore=List):
        self.meta_dict = meta_dict
        self.location = str(location)
        self.minprice = int(minprice)
        self.maxprice = int(maxprice)
        self.freshness = int(freshness)
        self.ignore = ignore

        self.listing_count = 0
        self.listing_ids = []
        self.listing_titles = []
        self.listing_urls = []
        self.listing_prices = []
        self.listing_date = self.load_seen_listings(SEEN_FILEPATH)

    def load_seen_listings(self, filepath):
        # Return dictionary of list_id: date
        try:
            with open(filepath) as csv_file:
                reader = csv.reader(csv_file)
                listing_dates = dict(reader)
                logging.info(f'Seen listings loaded from {filepath}')
        except FileNotFoundError:
            logging.warn(f'{filepath} does not exist.')
            listing_dates = {}
        return listing_dates

    def save_seen_listings(self, filepath):
        with open(filepath, 'a') as csv_file:
            writer = csv.writer(csv_file)
            for id in self.listing_ids:
                listing_date = min(TODAY, self.listing_date.get(id, TODAY))
                writer.writerow([id, listing_date])
        logging.info(f'Seen listings in {self.location} wrtten to {filepath}')

    def get_url(self, pageno):
        location_dict = self.meta_dict[self.location]
        if pageno == 1:
            pretext = 'https://www.propertyguru.com.sg/property-for-sale?market=residential&'
        else:
            pretext = f'https://www.propertyguru.com.sg/property-for-sale/{str(pageno)}?&'

        if location_dict['by'] == 'mrt':
            location_text = f'center_lat={str(location_dict["lat"])}&center_long={str(location_dict["long"])}&MRT_STATION={str(location_dict["MRT"])}&distance=1&freetext={location_dict["freetext"]}&'
        elif location_dict['by'] == 'district':
            location_text = f'&freetext={location_dict["freetext"]}&district_code[]={str(location_dict["district_code"])}&'
        else:
            location_text = ''
        recency_text = f'listing_posted={str(self.freshness)}&'
        buy_text = 'listing_type=sale&'
        price_text = f'minprice={str(self.minprice)}&maxprice={str(self.maxprice)}&'
        tenure_text = "tenure[]=F&tenure[]=L999&"
        type_text = "property_type=L&property_type_code[]=TERRA&property_type_code[]=DETAC&property_type_code[]=SEMI&property_type_code[]=CORN&property_type_code[]=LBUNG&property_type_code[]=BUNG&property_type_code[]=SHOPH&property_type_code[]=RLAND&property_type_code[]=TOWN&property_type_code[]=CON&property_type_code[]=LCLUS&"
        url = f'{pretext}{location_text}{buy_text}{recency_text}{price_text}{type_text}{tenure_text}search=true'
        return url

    def get_soup(self, pageno):
        url = self.get_url(pageno)
        attempt = 0
        # Try to connect to PropertyGuru a few times if rejected by Captcha challenge
        while attempt < MAX_ATTEMPTS:
            try:
                scraper = cloudscraper.create_scraper()
                page = scraper.get(url)
                break
            except cloudscraper.exceptions.CloudflareChallengeError:
                attempt += 1
                logging.info(f'Location {self.location}, Page {pageno}: Cloudscraper attempt {attempt} failed due to Captcha challenge.')
                time.sleep(2)
        soup = BeautifulSoup(page.content, "html.parser")
        logging.info(f'Location {self.location}, Page {pageno}: Successfully bypassed Cloudflare.')
        return soup

    def get_all_raw_listings(self):
        # This function gets the raw listings of all pages produced by the search
        # Get soup of the first search page
        soup = self.get_soup(1)
        self.get_page_raw_listings(soup)
        # There could be more than 1 page in the search result, need to find all of them
        paginations = soup.find_all('a', {'href': re.compile(r"/property-for-sale/*"), "data-page": re.compile(r"\d*")})
        # There could be 0 listings returned
        if paginations is None:
            paginations = []
        pagination = max([int(i['data-page']) for i in paginations] + [0])
        # If there are more than 1 pages
        if pagination > 1:
            pages = range(2, pagination+1)
            for j in pages:
                soup = self.get_soup(j)
                self.get_page_raw_listings(soup)

        logging.info(f'Location {self.location}: Found {self.listing_count} total listings.')
        return self.listing_ids, self.listing_titles, self.listing_urls

    def get_page_raw_listings(self, soup):
        # This function gets the raw listings of a single page related to the search
        listings = soup.find_all('div', {'class': re.compile(r"listing-card listing-id-*")})
        self.listing_count += len(listings)
        for listing in listings:
            if 'data-listing-id' not in listing.attrs:
                self.listing_count = 0
                return
            id = listing['data-listing-id']
            if TODAY - self.listing_date.get(id, TODAY) > timedelta(days=FRESHNESS_THRESHOLD):
                continue
            content = listing.find('a', {'href': re.compile(r"https://www\.propertyguru\.com\.sg/listing/*")})
            title = content['title'].replace("For Sale - ", "")
            # Check if we want to ignore this listing (from title)
            ignore = [re.search(case, title, re.IGNORECASE) for case in self.ignore]
            if not all(case is None for case in ignore):
                continue
            href = content['href']
            price = listing.find('span', {'class': 'price'}).contents[0]
            self.listing_ids.append(id)
            self.listing_titles.append(title)
            self.listing_urls.append(href)
            self.listing_prices.append(price)

    def wrap_listings_html(self):
        self.get_all_raw_listings()
        tbl = [self.listing_titles, self.listing_prices, self.listing_urls]
        tbl = list(map(list, itertools.zip_longest(*tbl, fillvalue=None)))
        tbl = tabulate(tbl, headers=["Title", "Price", "URL"], tablefmt='html')
        msg = f'<br></br><p><big><b>{self.location}</b>: {str(self.listing_count)} new listings out of {str(self.listing_count)} total listings.</big></p>'
        # Save seen listings
        self.save_seen_listings(SEEN_FILEPATH)
        return msg+tbl
