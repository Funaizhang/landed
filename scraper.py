from bs4 import BeautifulSoup
import cloudscraper
import re
from tabulate import tabulate
import itertools
import time
import logging
logging.basicConfig(level=logging.INFO)

MAX_ATTEMPTS = 10

class GuruScraper():
    def __init__(self, dict, location, minprice=3.1e6, maxprice=5.3e6, freshness=3):
        self.meta_dict = dict
        self.minprice = int(minprice)
        self.maxprice = int(maxprice)
        self.freshness = int(freshness)
        self.location = str(location)

        self.listing_count = 0
        self.listing_ids = []
        self.listing_titles = []
        self.listing_urls = []

    def get_url(self):
        location_dict = self.meta_dict[self.location]
        pretext = 'https://www.propertyguru.com.sg/property-for-sale?market=residential&'
        if location_dict['by'] == 'mrt':
            location_text = f'center_lat={str(location_dict["lat"])}&center_long={str(location_dict["long"])}&MRT_STATION={str(location_dict["MRT"])}&distance=1&freetext={location_dict["freetext"]}&'
        elif location_dict['by'] == 'district':
            location_text = f'&freetext={location_dict["freetext"]}&district_code[]={str(location_dict["district_code"])}&'
        else:
            location_text = f'listing_posted={str(location_dict["days"])}&'
        buy_text = 'listing_type=sale&'
        price_text = f'minprice={str(self.minprice)}&maxprice={str(self.maxprice)}&'
        tenure_text = "tenure[]=F&tenure[]=L999&"
        type_text = "property_type=L&property_type_code[]=TERRA&property_type_code[]=DETAC&property_type_code[]=SEMI&property_type_code[]=CORN&property_type_code[]=LBUNG&property_type_code[]=BUNG&property_type_code[]=SHOPH&property_type_code[]=RLAND&property_type_code[]=TOWN&property_type_code[]=CON&property_type_code[]=LCLUS&"
        url = f'{pretext}{location_text}{buy_text}{price_text}{type_text}{tenure_text}search=true'
        return url

    def get_soup(self):
        url = self.get_url()
        print(url)
        attempt = 0
        while attempt < MAX_ATTEMPTS:
            try:
                scraper = cloudscraper.create_scraper()
                page = scraper.get(url)
                break
            except cloudscraper.exceptions.CloudflareChallengeError:
                attempt += 1
                logging.info(f'Location {self.location}: Cloudscraper attempt {attempt} failed due to Captcha challenge.')
                time.sleep(5)
        soup = BeautifulSoup(page.content, "html.parser")
        logging.info(f'Location {self.location}: Successfully bypassed Cloudflare.')
        return soup

    def get_raw_listings(self):
        soup = self.get_soup()
        listings = soup.find_all('div', {'class': re.compile(r"listing-card listing-id-*")})
        self.listing_count = len(listings)
        for listing in listings:
            id = listing['data-listing-id']
            content = listing.find('a', {'href': re.compile(r"https://www\.propertyguru\.com\.sg/listing/*")})
            title = content['title'].replace("For Sale - ", "")
            href = content['href']
            self.listing_ids.append(id)
            self.listing_titles.append(title)
            self.listing_urls.append(href)
        logging.info(f'Location {self.location}: Found {self.listing_count} total listings.')
        return self.listing_ids, self.listing_titles, self.listing_urls

    def wrap_listings_html(self):
        self.get_raw_listings()
        table = [self.listing_titles, self.listing_urls]
        table = list(map(list, itertools.zip_longest(*table, fillvalue=None)))
        tbl = tabulate(table, headers=["Title", "URL"], tablefmt='html')
        msg = f'<br></br><p><big><b>{self.location}</b>: {str(self.listing_count)} new listings out of {str(self.listing_count)} total listings.</big></p>'
        return msg+tbl
