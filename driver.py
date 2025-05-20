import argparse
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from review_scraper import ReviewSpider
import threading
import time

#class used to signal spider to stop crawling and yield items
class YieldTrigger:
    def __init__(self, delay=5):
        self.delay = delay
        self._triggered = False
        self._thread = None

    def schedule_trigger(self):
        #Schedule the yield trigger after delay seconds
        self._thread = threading.Thread(target=self._wait_and_trigger)
        self._thread.daemon = True
        self._thread.start()

    def _wait_and_trigger(self):
        #Wait for delay
        time.sleep(self.delay)

        #alter trigger flag
        self._triggered = True
        print(f"\nYield trigger activated after {self.delay} seconds")

    #function to check status of trigger flag
    def was_triggered(self):
        return self._triggered

#function to parse command line args
def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--product_name', 
        type=str, 
        default="", 
        help='best buy product name'
    )
    parser.add_argument(
        '--id_num', 
        type=str, 
        default="0000000", 
        help='seven digit product id'
    )
    parser.add_argument(
        '--trigger_delay', 
        type=int, 
        default=5, 
        help='delay in seconds before triggering item yield'
    )

    return parser.parse_args()

def run_spider(name=None, id=None, trigger_delay=5):
    process = CrawlerProcess(get_project_settings())
    yield_trigger = YieldTrigger(trigger_delay)
    
    #Schedule the yield trigger
    yield_trigger.schedule_trigger()
    
    #handler function for spider instance
    def spider_runner():
        spider = ReviewSpider(prod_name=name, prod_num=id)
        spider.yield_trigger = yield_trigger
        return spider
    
    #Pass the spider class with specified args
    process.crawl(
        ReviewSpider,
        prod_name=name,
        prod_num=id,
        spider_runner=spider_runner
    )
    
    process.start()

def main():
    print("Starting Spider Process")
    args = parse_args()
    run_spider(name=args.product_name, id=args.id_num, trigger_delay=args.trigger_delay)
    print("Spider Process Completed")

if __name__ == "__main__":
    main()