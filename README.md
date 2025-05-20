# Backcountry Scheduled Price Monitor
Web scraper implemented in python using scrapy designed to pull all reviews of a specified product listing on bestbuy.com.

# USAGE
python driver.py --product_name <product name from url> --id_num <sku from url> --trigger_delay <seconds spider should scrape for>

NAME ARG: specific product listing name from the bestbuy listing url eg: hp-laserjet-pro-mfp-3301sdw-wireless-color-all-in-one-laser-printer-white

ID ARG: sku id number from listing url eg: 6582284

DELAY ARG: scraper will continue to pull listings for the specified duration in seconds before yielding all scraped items

# OUTPUT
The output is in the form of a csv file. One item is created in the csv file for each review scraped from the site.
Each item contais data on the rating, the reviwer name, the date of the review, review title, whether or not a purchase
has been verified, and of course the actual body of the review.

# PROBLEMS/SOLUTIONS
Yield Trigger: The yield trigger exists as a work around for the strange behavior I was getting from an older version of the script.
The script would stall and not produce anything, until it was forced to shut down, at which point it would suddenly produce items
before doing so. The yield trigger was devised as a way to mimic a SIGINT sent to the spider code by having the driver code signal the spider
to stop looking for new listings and yield the results it has obtained. The specific delay in seconds is controllable via a command line argument,

Browser/User Agent: The user agent and browser that I used for the scheduled price monitor project did not prove to be sufficient for this case.
The mozilla user agent I was using seemingly did not past muster for best buy bot prevention, and also seemingly had trouble rendering certain aspects
of the html. These issues were fixed via the use of a playwright browser.

