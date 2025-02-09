import scrapy


class MoviesSpider(scrapy.Spider):
    name = "movies"
    allowed_domains = ["ru.wikipedia.org"]
    start_urls = ["https://ru.wikipedia.org/wiki/%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%A4%D0%B8%D0%BB%D1%8C%D0%BC%D1%8B_%D0%BF%D0%BE_%D0%B0%D0%BB%D1%84%D0%B0%D0%B2%D0%B8%D1%82%D1%83"]

    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'movies.csv'
    }

    def parse(self, response):
        for selector in response.css('div.mw-category-group li a::attr(href)').getall():
            yield response.follow(selector, self.parse_movies)
        
        next_page = response.xpath('//a[contains(text(), "Следующая страница")]/@href').extract_first()
        if next_page:
            yield response.follow(next_page, self.parse)
    
    def parse_movies(self, response):
        infobox = response.css('table.infobox')
        
        if infobox:
            yield {
                'title': response.css('th.infobox-above::text').get(default='').strip(),
                'genre': response.xpath('//*[@data-wikidata-property-id="P136"]//text()').getall(),
                'director': self.extract_info(infobox, ['Режиссёр', 'Режиссеры']),
                'country': self.extract_info(infobox, ['Страна', 'Страны']),
                'year': self.extract_info(infobox, ['Год'])
            }
        else:
            self.logger.warning(f"Inbox not found for {response.url}")

    def extract_info(self, infobox, labels):
        info = []
        for label in labels:
            info.extend(infobox.xpath(f'.//th[contains(text(), "{label}")]/following-sibling::td//text()').getall())
        
        cleaned_info = [text.strip() for text in info if text.strip()]
        return ', '.join(cleaned_info)
    