# addforums_scraper
http://www.addforums.com/forums/index.php scraper.

Requires scrapy and python 2.7

http://doc.scrapy.org/en/latest/intro/install.html - install docs for scrapy

To put our spider to work, go to the project’s top level directory and run:

scrapy crawl addforums -t csv -o addforums.csv --loglevel=INFO
