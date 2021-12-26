from mail import EmailSender
from scraper import GuruScraper

if __name__ == '__main__':
    myGuruScraper = GuruScraper()
    html_table = myGuruScraper.run('Upper Thomson')

    myEmailSender = EmailSender(sender="@gmail.com",
                                receivers=["@gmail.com"])
    myEmailSender.send_email(subject="Daily new property listings", message=html_table)