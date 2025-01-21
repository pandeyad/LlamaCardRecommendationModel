from webcrawler import BaseCrawler


class BankCrawler(BaseCrawler):

    def __init__(self, **kwargs):
        pass

    def _get_credit_cards_url(self):
        raise Exception("Please extend this method for bank crawler")

    def crawl_data(self, **kwargs):
        bank = kwargs['bank']
        for url in self._get_credit_cards_url():
            self._crawl_credit_card_data(bank, url)

    def _crawl_credit_card_data(self, bank, card_url):
        raise Exception("Please extend this method for bank crawler")


    def _collate_credit_card_contents(self, title, description, directory, **kwargs):
        with open(f'{directory}{title}.md', 'w+', encoding='utf-8') as md_file:
            md_file.write(f"# {title}\n\n")
            md_file.write(description)
            md_file.write("\n\n")
            self._write_content(md_file, **kwargs)
        md_file.close()


    def _write_content(self, fp, **kwargs):
        raise Exception("This method needs to be extended.")


