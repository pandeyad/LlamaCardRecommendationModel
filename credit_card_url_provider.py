from webcrawler.bank.hdfc import HDFCBankCrawler

def get_urls():
    return HDFCBankCrawler()._get_credit_cards_url()