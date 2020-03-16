# -*- coding: utf-8 -*-
import scrapy
from handle_mongo import mongo
import re
from ..items import GuaziScrapyProjectItem



class GuaziSpider(scrapy.Spider):

    name = 'guazi'
    allowed_domains = ['guazi.com']

    def start_requests(self):
        while True:
            task = mongo.get_task('guazi_task')
            print('获取task：%s' % task)
            #task取空了，就停下来
            if not task:
                break
            # 列表页
            if task['item_type'] == 'list_item':
                yield scrapy.Request(
                    url=task['task_url'],
                    dont_filter = True,
                    callback= self.handle_car_item,
                    errback= self.handle_err,
                    meta = task,
                    encoding='utf-8'
                )
            # 详情页
            elif task['item_type'] == 'car_info_item':
                yield scrapy.Request(url=task['car_url'],callback=self.handle_car_info,dont_filter=True,
                                     meta=task,errback=self.handle_err)


    def handle_err(self,failure):
        '''报错回调方法'''
        print('出错，待补充')
        print(failure)
        return


    def handle_car_item(self,response):
        '''解析详汽车列表'''
        print('获取到汽车列表')
        car_item_list = response.xpath("//ul[@class='carlist clearfix js-top']/li")
        print(car_item_list)
        for car_item in car_item_list:
            car_list_info = {}
            car_list_info['car_name'] = car_item.xpath("./a/h2/text()").extract_first()
            car_list_info['car_url'] = 'https://www.guazi.com'+car_item.xpath("./a/@href").extract_first()
            car_list_info['item_type'] = 'car_info_item'
            yield scrapy.Request(url=car_list_info['car_url'],callback=self.handle_car_info,
                                 dont_filter=True,meta=car_list_info,errback=self.handle_err)

        if response.xpath("//ul[@class='pageLink clearfix']/li[last()]//span/text()").extract_first() == '下一页':
            # https: // www.guazi.com / www / toyota / o2c - 1 /
            value_search = re.compile("https://www.guazi.com/www/(.*?)/o(\d+)c-1")
            try:
                value = value_search.findall(response.url)[0]
                response.request.meta['task_url'] = 'https://www.guazi.com/www/%s/o%sc-1' % (value[0],
                                                                                             str(int(value[1]) + 1))
                yield scrapy.Request(url=response.request.meta['task_url'], callback=self.handle_car_item,
                                     meta=response.request.meta, dont_filter=False, errback=self.handle_err)
            except:
                print('获取下一页失败',response.request.meta['task_url'])


    def handle_car_info(self,response):
        '''解析汽车详情页'''
        print('获取汽车数据')
        car_id_search = re.compile(r"车源号：(.*?)\s+")
        car_info = GuaziScrapyProjectItem()
        #car_id
        car_info['car_id'] = car_id_search.search(response.text).group(1)
        car_info['car_name'] = response.request.meta['car_name']
        car_info['from_url'] = response.request.meta['car_url']
        car_info['car_price'] = response.xpath("//span[@class='pricestype']/text()").extract_first().strip()+'万'
        car_info['license_time'] = response.xpath("//ul[@class='assort clearfix']/li[@class='one']/span/text()").extract_first().strip()
        car_info['km_info'] = response.xpath("//ul[@class='assort clearfix']/li[@class='two']/span/text()").extract_first().strip()
        car_info['license_location'] = response.xpath("//ul[@class='assort clearfix']/li[@class='three']/span/text()").extract()[0].strip()
        # 排量信息
        car_info['desplacement_info'] = response.xpath("//ul[@class='assort clearfix']/li[@class='three']/span/text()").extract()[-1].strip()
        # 变速箱，手动挡还是自动挡
        car_info['transmission_case'] = response.xpath("//ul[@class='assort clearfix']/li[@class='last']/span/text()").extract_first().strip()
        yield car_info
