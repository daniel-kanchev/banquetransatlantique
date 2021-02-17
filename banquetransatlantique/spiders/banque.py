import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from banquetransatlantique.items import Article


class BanqueSpider(scrapy.Spider):
    name = 'banque'
    start_urls = ['https://www.banquetransatlantique.com/fr/index.html']

    def parse(self, response):
        articles = response.xpath('//section//article')
        for article in articles:
            link = article.xpath('.//a[@class="more"]/@href').get()
            date = article.xpath('.//time/text()').get()
            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

    def parse_article(self, response, date):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = " ".join(response.xpath('//h1//text()').getall())
        if title:
            title = title.strip()

        if date:
            date = datetime.strptime(date.strip(), '%d/%m/%Y')
            date = date.strftime('%Y/%m/%d')

        content = response.xpath('//div[@itemprop="articleBody"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
