import scrapy
import json

class ProductSpider(scrapy.Spider):
    name = 'products'
    start_urls = ['https://www.katapulk.com/']

    @staticmethod
    def clean_spaces(string: str):
        ''' Remove leading, trailing and multiple whitespaces in string'''
        return ' '.join(string.split())

    def parse(self, response):
        products = response.css('div.src-components-styles-components-___product-tile__textBlock___286s4')
        recognized_products = dict()
        for product in products:
            title = ProductSpider.clean_spaces(product.css('h4.src-components-styles-components-___product-tile__titleCard___3kCr3 a::text').get())
            description = ProductSpider.clean_spaces(product.css('div.src-components-styles-components-___product-tile__productDescription___3Imvy p::text').get())
            price = ProductSpider.clean_spaces(product.css('div.src-components-styles-components-___product-tile__price___249i-::text').get())
            relative_url = product.css('h4.src-components-styles-components-___product-tile__titleCard___3kCr3 a::attr(href)').get()
            url = None if relative_url is None else response.urljoin(relative_url)
            recognized_products[title+price] = dict(title=title, description=description, price=price, url=url)

        filename = 'products.json'
        with open(filename, 'w') as f:
            json.dump(recognized_products, f, indent=4)
        self.log(f'Saved {len(recognized_products)} products to {filename}')
