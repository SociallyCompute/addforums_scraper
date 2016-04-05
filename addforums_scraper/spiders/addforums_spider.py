import scrapy
import w3lib.url
from addforums_scraper.processors import to_int
from addforums_scraper.items import PostItem
import re
import logging
import datetime


class AddforumsSpider(scrapy.Spider):
    name = 'addforums'
    allowed_domains = ['addforums.com']
    start_urls = ["http://www.addforums.com/forums/index.php"]

    patterns = {'thread_id': re.compile('t=(\d+)'),
                'next_page_url': "//*[@class='pagenav']//*[@href and contains(text(), '>')]/@href",
                'post_id': re.compile('p=(\d+)')}

    def parse(self, response):
        forum_urls = response.xpath('.//td[contains(@id,"f")]/div/a/@href').extract()
        for url in forum_urls:
            url = w3lib.url.url_query_cleaner(url, ['s'], remove=True)
            yield scrapy.Request(response.urljoin(url), callback=self.parse_forum)

    def parse_forum(self, response):
        logging.info("STARTING NEW FORUM SCRAPE (GETTING THREADS)")
        thread_urls = response.xpath('.//a[contains(@id,"thread_title")]/@href').extract()

        for url in thread_urls:
            yield scrapy.Request(response.urljoin(url), callback=self.parse_posts, priority=1)

        # check subforums
        if 'paginate' not in response.meta:
            forum_urls = response.xpath('.//td[contains(@id,"f")]//td/div/a/@href').extract()
            for url in forum_urls:
                url = w3lib.url.url_query_cleaner(url, ['s'], remove=True)
                yield scrapy.Request(response.urljoin(url), callback=self.parse_forum)

        # return the next forum page if it exists
        yield self.paginate(response, next_page_callback=self.parse_forum)

    def parse_posts(self, response):
        logging.info("STARTING NEW PAGE SCRAPE")

        if 'posts_scraped' in response.meta:
            posts_scraped = response.meta['posts_scraped']
        else:
            posts_scraped = []

        title = ''
        title_list = response.xpath('.//td[@class="navbar"]/strong/text()').extract()
        if title_list is not None:
            title_list = [unicode.strip(t) for t in title_list if unicode.strip(t)]
            title = ' '.join(title_list)

        today = datetime.datetime.utcnow() - datetime.timedelta(hours=4)
        yesterday = today - datetime.timedelta(days=1)

        if response.xpath('.//div[@class="pagenav"]//a').extract_first() is not None:
            pagination = True
        else:
            pagination = False

        for post in response.xpath("//table[contains(@id,'post')]"):
            p = PostItem()

            p['qid'] = to_int(re.findall(self.patterns['thread_id'], response.url)[0])
            p['localID'] = to_int(post.xpath(".//tr/td/div[@class='normal'][1]/a//text()").extract_first()) - 2
            id = post.xpath(".//tr/td/div[@class='normal'][1]/a/@href").extract_first()
            id = to_int(re.findall(self.patterns['post_id'], id)[0])
            p['uniqueID'] = str(p['qid']) + '_'
            p['uniqueID'] += 'top' if p['localID'] == -1 else str(p['localID'])

            p['title'] = title

            p['poster'] = post.xpath(".//a[@class='bigusername']//text()").extract_first()

            p_datetime = post.xpath("string(.//tr/td/div[@class='normal'][2])").extract_first().strip()
            p_datetime = re.sub("^Yesterday", yesterday.strftime('%m-%d-%y'), p_datetime)
            p_datetime = re.sub("^Today", today.strftime('%m-%d-%y'), p_datetime)
            p_datetime = datetime.datetime.strptime(p_datetime, "%m-%d-%y, %I:%M %p")
            p['date'] = p_datetime.strftime("%m/%d/%Y %H:%M:%S")

            posts_scraped.append((id, p['uniqueID'], p['poster']))

            replyTo = ''
            inferred_replies = ''
            if p['localID'] != -1:
                quote = post.xpath(".//div[div[text()='Quote:']]")
                reply_to_id = quote.xpath(".//a[img[contains(@class, 'inlineimg')]]/@href").extract_first()
                if reply_to_id:
                    reply_to_id = to_int(re.findall(self.patterns['post_id'], reply_to_id)[0])
                    reply_to_post = next((item for item in posts_scraped if item[0] == reply_to_id), None)
                    if reply_to_post:
                        replyTo = reply_to_post[1]
                        inferred_replies = reply_to_post[2]
                else:
                    replyTo = posts_scraped[0][1]
                    inferred_replies = posts_scraped[0][2]
            p['replyTo'] = replyTo

            p['inferred_replies'] = inferred_replies

            content_list = post.xpath(".//*[contains(@id,'post_message_')]//text()[not(ancestor::div[div[text()='Quote:']])]").extract()
            content_list = [unicode.strip(s) for s in content_list if unicode.strip(s)]
            p['content'] = ' '.join(content_list)

            yield p

        if pagination:
            yield self.paginate_posts(response, next_page_callback=self.parse_posts, posts_scraped=posts_scraped)

    def paginate(self, response, next_page_callback):
        """Returns a scrapy.Request for the next page, or returns None if no next page found.
        response should be the Response object of the current page."""
        next_page = response.xpath(self.patterns['next_page_url'])

        if next_page:
            url = response.urljoin(next_page.extract_first())
            logging.info("NEXT PAGE IS: %s" % url)
            request = scrapy.Request(url, next_page_callback)
            request.meta['paginate'] = True
            return request
        else:
            return None

    def paginate_posts(self, response, next_page_callback, posts_scraped=None):
        """Returns a scrapy.Request for the next page, or returns None if no next page found.
        response should be the Response object of the current page."""
        next_page = response.xpath(self.patterns['next_page_url'])

        if next_page:
            url = response.urljoin(next_page.extract_first())
            logging.info("NEXT PAGE IS: %s" % url)
            request = scrapy.Request(url, next_page_callback, priority=10)
            if posts_scraped is not None:
                request.meta['posts_scraped'] = posts_scraped
            return request
        else:
            return None
