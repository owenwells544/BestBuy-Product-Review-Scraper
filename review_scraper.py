import scrapy
import json
from urllib.parse import urljoin

class ReviewSpider(scrapy.Spider):
    name = "bestbuy_reviews"
    CSV_FILE = 'bestbuytest.csv'

    #specify browser type and output formatting
    custom_settings = {
        'PLAYWRIGHT_BROWSER_TYPE': 'chromium',
        'FEEDS': {
            CSV_FILE: {
               'format': 'csv',
                'encoding': 'utf-8',
                'overwrite': True
            },
        }
    }

    def __init__(self, prod_name=None, prod_num=None, spider_runner=None, **kwargs):
        #retrieve args passed from driver code
        self.p_name = prod_name
        self.p_num = prod_num
        self.start_urls = [f'https://www.bestbuy.com/site/reviews/{self.p_name}/{self.p_num}']
        
        #handler yield trigger from driver code
        if spider_runner:
            spider_instance = spider_runner()
            self.yield_trigger = getattr(spider_instance, 'yield_trigger', None)
        else:
            self.yield_trigger = None
            
        self.trigger_activated = False
        super().__init__(**kwargs)
    
    def parse(self, response):
        #check if yield trigger was activated
        if self.yield_trigger and self.yield_trigger.was_triggered() and not self.trigger_activated:
            self.logger.info("Yield trigger detected - forcing item processing")
            self.trigger_activated = True
        
        reviews = response.css('li.review-item')
        
        if not reviews:
            if self.trigger_activated:
                self.logger.info("No reviews found even after trigger - giving up")
                return
            self.logger.warning("No reviews found - waiting for trigger")
            return

        for r in reviews:
            #get json containing product reviews
            json_data = r.css('script[type="application/ld+json"]::text').get()
            rating = 0
            if json_data:
                try:
                    #extract review data and parse review rating
                    data = json.loads(json_data)
                    rating = data.get('reviewRating', {}).get('ratingValue', 0)
                except json.JSONDecodeError:
                    pass
            
            #yield one review item for output to csv
            yield {
                'rating': rating,
                'reviewer_name': r.css('div.ugc-author strong::text').get('').strip(),
                'review_date': r.css('time.submission-date::attr(title)').get('').strip(),
                'review_title': r.css('h4.review-title::text').get('').strip(),
                'review_body': r.css('div.ugc-review-body p::text').get('').strip(),
                'verified_purchase': bool(r.css('button:contains("Verified Purchase")'))
            }
        
        #pagination handling
        next_page = response.css('a.next-page::attr(href)').get()
        if next_page:
            yield response.follow(
                next_page,
                callback=self.parse,
                meta={
                    'handle_httpstatus_list': [403, 404, 429],
                    'dont_redirect': True
                }
            )