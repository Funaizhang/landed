from bs4 import BeautifulSoup
import cloudscraper
import re


class GuruScraper():
    def __init__(self):
        self.meta_dict = {
            'Upper Thomson': {'lat': 1.3539717, 'long': 103.8338127, 'MRT': 8193, 'freetext': 'TE8+Upper+Thomson+MRT+Station'},
            'Tan Kah Kee': {'lat': 0.0, 'long': 0.0, 'MRT': 0, 'freetext': ''},
            'Marine Parade': {'lat': 0.0, 'long': 0.0, 'MRT': 0, 'freetext': ''}
        }
        self.minprice = int(3e6)
        self.maxprice = int(5.5e6)
        self.listing_count = 0
        self.listing_ids = []
        self.listing_titles = []
        self.listing_urls = []

        self.sender_email = "naifuzhang@gmail.com"
        self.receiver_email = "naifuzhang@gmail.com"

    def get_url(self, location):

        location_dict = self.meta_dict[location]
        pretext = 'https://www.propertyguru.com.sg/property-for-sale?market=residential'
        location_text = f'center_lat={str(location_dict["lat"])}&center_long={str(location_dict["long"])}&MRT_STATION={str(location_dict["MRT"])}&distance=1&freetext={location_dict["freetext"]}'
        buy_text = 'listing_type=sale'
        price_text = f'minprice={str(self.minprice)}&maxprice={str(self.maxprice)}'
        tenure_text = "tenure[]=F&tenure[]=L999"
        type_text = "property_type=L&property_type_code[]=TERRA&property_type_code[]=DETAC&property_type_code[]=SEMI&property_type_code[]=CORN&property_type_code[]=LBUNG&property_type_code[]=BUNG&property_type_code[]=SHOPH&property_type_code[]=RLAND&property_type_code[]=TOWN&property_type_code[]=CON&property_type_code[]=LCLUS"
        url = f'{pretext}&{location_text}&{buy_text}&{price_text}&{type_text}&{tenure_text}&search=true'
        return url

    def get_html(self, url):
        scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance
        page = scraper.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        return soup

    def get_listings(self, soup):
        listings = soup.find_all('div', {'class': re.compile(r"listing-card listing-id-*")})
        self.listing_count = len(listings)
        for listing in listings:
            id = listing['data-listing-id']
            content = listing.find('a', {'href': re.compile(r"https://www\.propertyguru\.com\.sg/listing/*")})
            title = content['title']
            href = content['href']
            self.listing_ids.append(id)
            self.listing_titles.append(title)
            self.listing_urls.append(href)
        return

if __name__ == '__main__':
    myGuruScraper = GuruScraper()
    URL = myGuruScraper.get_url('Upper Thomson')
    html = myGuruScraper.get_html(URL)
    myGuruScraper.get_listings(html)
    for i in range(myGuruScraper.listing_count):
        print(f'id: {myGuruScraper.listing_ids[i]}; title: {myGuruScraper.listing_titles[i]}; url: {myGuruScraper.listing_urls[i]}')
