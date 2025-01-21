class BaseCrawler:

    def crawl_data(self, **kwargs):
        raise Exception("Unsupported method. Please extend this method.")


    def get_base_data_path(self):
        return '/Users/adityapandey/workspace/LlamaCardRecommendationModel/data/'