from mail import EmailSender
from scraper import GuruScraper

if __name__ == '__main__':
    locations = ['Upper Thomson', 'Tan Kah Kee', 'Marine Parade']
    myGuruScraper = GuruScraper(locations)
    html_table = myGuruScraper.run()

    myEmailSender = EmailSender(sender="@gmail.com",
                                receivers=["@gmail.com"])
    myEmailSender.send_email(subject="Daily new listings", message=''.join(html_table))