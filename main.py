from mail import EmailSender
from scraper import GuruScraper
from datetime import datetime

min_price = 3e6
max_price = 5.3e6
freshness = 3
meta_dict = {
    'Upper Thomson':     {'lat': 1.3539717, 'long': 103.8338127, 'MRT': 8193, 'freetext': 'TE8+Upper+Thomson+MRT+Station', 'by': 'mrt'},
    'Bright Hill':       {'lat': 1.3618059, 'long': 103.8320631, 'MRT': 8192, 'freetext': 'TE7+Bright+Hill+MRT+Station', 'by': 'mrt'},
    'Tan Kah Kee':       {'lat': 1.3257996, 'long': 103.8079556, 'MRT': 2018, 'freetext': 'DT8+Tan+Kah+Kee+MRT+Station', 'by': 'mrt'},
    'Sixth Avenue':      {'lat': 1.3311776, 'long': 103.7972016, 'MRT': 2021, 'freetext': 'DT7+Sixth+Avenue+MRT+Station', 'by': 'mrt'},
    'King Albert Park':  {'lat': 1.3356884, 'long': 103.7831926, 'MRT': 2024, 'freetext': 'DT6+King+Albert+Park+MRT+Station', 'by': 'mrt'},
    'Marine Parade':     {'lat': 1.3030169, 'long': 103.905723, 'MRT': 8322, 'freetext': 'TE26+Marine+Parade+MRT+Station', 'by': 'mrt'},
    'Marine Terrace':    {'lat': 1.3069297, 'long': 103.915745, 'MRT': 8323, 'freetext': 'TE27+Marine+Terrace+MRT+Station', 'by': 'mrt'},
    'D20 Thomson':       {'district_code': 'D20', 'freetext': 'D20+Ang+Mo+Kio+/+Bishan+/+Thomson', 'by': 'district'},
    'D11 Newton/Novena': {'district_code': 'D11', 'freetext': 'D11+Newton+/+Novena', 'by': 'district'},
    'D10 Bukit Timah':   {'district_code': 'D10', 'freetext': 'D10+Tanglin+/+Holland+/+Bukit+Timah', 'by': 'district'},
    'D15 East Coast':    {'district_code': 'D15', 'freetext': 'D15+East+Coast+/+Marine+Parade', 'by': 'district'},
    'All': {'days': freshness, 'by': ''},
    }

if __name__ == '__main__':
    locations = meta_dict.keys()
    myGuruScrapers = [GuruScraper(meta_dict, i, minprice=min_price, maxprice=max_price) for i in locations]
    htmls = [i.wrap_listings_html() for i in myGuruScrapers]

    today = datetime.today().strftime('%Y-%m-%d')
    myEmailSender = EmailSender(sender="@gmail.com",
                                receivers=["@gmail.com"])
    myEmailSender.send_email(subject=f'New listings on {today}', message=''.join(htmls))