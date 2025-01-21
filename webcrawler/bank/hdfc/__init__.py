from webcrawler.bank import BankCrawler
import requests
from bs4 import BeautifulSoup
import os


class HDFCBankCrawler(BankCrawler):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _get_credit_cards_url(self):
        credit_cards_info = 'https://www.hdfcbank.com/personal/pay/cards/credit-cards'
        try:
            # Fetch the HTML content of the given URL
            response = requests.get(credit_cards_info)
            response.raise_for_status()
            html_content = response.text

            # Parse the HTML using BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            all_ = soup.find_all('a', {'title': 'Know More'})
            urls = []
            for i in all_:
                urls.append(f"https://www.hdfcbank.com{i.get('href')}")
            return list(set(urls))
        except Exception as e:
            print(f"An error occurred: {e}")

    def _crawl_features(self, content):
        return

    def _crawl_eligibility(self, content):
        return

    def _crawl_charges(self, content):
        return

    def _get_html_content(self, url):
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text
        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup

    def _get_content(self, url):
        try :
            soup = self._get_html_content(url)
            accordion = soup.find(attrs={'class': 'accordion'})
            return self.transform_data(accordion)
        except:
            return "Nothing specific"

    def transform_data(self, content: BeautifulSoup):
        data = ""
        rows = content.find_all(attrs={'class': 'row content-body'})
        for row in rows:
            inner_rows = row.find_all(name='div', recursive=False)
            # Assuming that if the length is > 2, the first is title
            if len(inner_rows) >= 2:
                text = [inner_rows[0].get_text().strip().split("\n")[0].replace(" ", " ").replace("​", " ")]
                for i in inner_rows[1].find_all(recursive=False):
                    c = i.get_text().strip().replace(" ", " ").replace("​", " ")
                    if c:
                        try:
                            if c not in text:
                                text.append(c)
                        except:
                            continue
                data = data + "####" + text[0] + "\n" + "\n".join(text[1:]) + "\n\n"
            elif len(inner_rows) == 1:
                data = inner_rows[0].get_text().strip().replace(" ", " ").replace("​", " ") + "\n\n"
        return data

    def _write_content(self, fp, **kwargs):
        for title, content in kwargs.items():
            fp.write(f"## {title.upper()}\n")
            fp.write(f"{content}")
            fp.write("\n\n")

    def _crawl_credit_card_data(self, bank, card_url):
        try:
            print(f"Getting data for {card_url}")
            content = {
                'Features' : self._get_content(card_url),
                'Eligibility' : self._get_content(card_url + '/eligibility'),
                'Fees and charges' : self._get_content(card_url + "/fees-and-charges"),
                'Activation Steps' : self._get_content(card_url + "/activation-steps")
            }
            directory = f'{self.get_base_data_path()}hdfc/'

            os.makedirs(directory, exist_ok=True)  # Create the directory if it doesn't exist
            description = self._get_html_content(card_url).find(attrs={'class':'be-ex-article widget-bg-color simple-plain-text'})
            self._collate_credit_card_contents(directory=directory,
                                               title=card_url.split('/')[-1].replace('-', ' ').upper(),
                                               description=description.get_text() if description else 'This is a credit card provided by HDFC bank. Please find the details related to this credit card below.',
                                               **content)
        except Exception as err:
            print(f"Error fetching the content: {err}")
            raise err


if __name__ == "__main__":
    HDFCBankCrawler(bank='hdfc').crawl_data(bank='hdfc')
