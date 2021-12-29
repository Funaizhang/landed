from bs4 import BeautifulSoup
import cloudscraper
import re
from tabulate import tabulate
import itertools

class GuruScraper():
    def __init__(self, locations):
        self.meta_dict = {
            'Upper Thomson':  {'lat': 1.3539717, 'long': 103.8338127, 'MRT': 8193, 'freetext': 'TE8+Upper+Thomson+MRT+Station', 'by': 'mrt'},
            'Bright Hill':    {'lat': 1.3618059, 'long': 103.8320631, 'MRT': 8192, 'freetext': 'TE7+Bright+Hill+MRT+Station', 'by': 'mrt'},
            'Tan Kah Kee':    {'lat': 1.3257996, 'long': 103.8079556, 'MRT': 2018, 'freetext': 'DT8+Tan+Kah+Kee+MRT+Station', 'by': 'mrt'},
            'Sixth Avenue':   {'lat': 1.3311776, 'long': 103.7972016, 'MRT': 2021, 'freetext': 'DT7+Sixth+Avenue+MRT+Station', 'by': 'mrt'},
            'KAP':            {'lat': 1.3356884, 'long': 103.7831926, 'MRT': 2024, 'freetext': 'DT6+King+Albert+Park+MRT+Station', 'by': 'mrt'},
            'Marine Parade':  {'lat': 1.3030169, 'long': 103.905723, 'MRT': 8322, 'freetext': 'TE26+Marine+Parade+MRT+Station', 'by': 'mrt'},
            'Marine Terrace': {'lat': 1.3069297, 'long': 103.915745, 'MRT': 8323, 'freetext': 'TE27+Marine+Terrace+MRT+Station', 'by': 'mrt'},
            'D20 Thomson':       {'district_code': 'D20', 'freetext': 'D20+Ang+Mo+Kio+/+Bishan+/+Thomson', 'by': 'district'},
            'D11 Newton/Novena': {'district_code': 'D11', 'freetext': 'D11+Newton+/+Novena', 'by': 'district'},
            'D10 Bukit Timah':   {'district_code': 'D10', 'freetext': 'D10+Tanglin+/+Holland+/+Bukit+Timah', 'by': 'district'},
            'D15 East Coast':    {'district_code': 'D15', 'freetext': 'D15+East+Coast+/+Marine+Parade', 'by': 'district'},
            'All': {'days': 3, 'by': ''},
        }

        self.minprice = int(3.1e6)
        self.maxprice = int(5.3e6)
        self.locations = locations

    def cleanup(self):
        self.listing_count = 0
        self.listing_ids = []
        self.listing_titles = []
        self.listing_urls = []

    def get_url(self, location):
        location_dict = self.meta_dict[location]
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

    def get_soup(self, loc):
        url = self.get_url(loc)
        scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance
        page = scraper.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        return soup

    def get_listings(self, loc):
        soup = self.get_soup(loc)
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
        return self.listing_ids, self.listing_titles, self.listing_urls

    def wrap_listings_html(self, loc):
        table = [self.listing_titles, self.listing_urls]
        table = list(map(list, itertools.zip_longest(*table, fillvalue=None)))
        tbl = tabulate(table, headers=["Title", "URL"], tablefmt='html')
        msg = f'<p></p><p><big><b>{str(loc)}</b>: {str(self.listing_count)} new listings out of {str(self.listing_count)} total listings.</big></p>'
        return msg+tbl

    def run(self):
        html_objs = []
        for loc in self.locations:
            self.cleanup()
            self.get_listings(loc)
            html_objs.append(self.wrap_listings_html(loc))
        return html_objs
