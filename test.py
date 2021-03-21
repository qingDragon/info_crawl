import datetime
import json
import os

import requests
from bs4 import BeautifulSoup

today = datetime.date.today().strftime('%Y%m%d')

def crawl_wiki_data():
    """
    爬取百度百科中《青春有你2》中选手信息，返回html
    :return:
    """
    headers = {
        'User-Agent':'Mozilla/5.0(Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }
    url = 'https://baike.baidu.com/item/青春有你第二季'
    try:
        response = requests.get(url,headers = headers)
        print(response.status_code)

        soup = BeautifulSoup(response.text,'lxml')
        tables = soup.find_all('table', {'log-set-param':'table_view'})
        crawl_table_title = "选手排名"


        for table in tables:

            table_titles = table.find_previous('div').find_all('h3')
            for title in table_titles:
                if(crawl_table_title in title):
                    print(table)
                    return table
    except Exception as e:
        print(e)

def parse_wiki_data(table_html):

    bs = BeautifulSoup(str(table_html),'lxml')
    all_trs = bs.find_all('tr')

    error_list = ['\'','\"']

    stars = []

    for tr in all_trs[1:]:
        all_tds = tr.find_all('td')

        star = {}

        star["name"] = all_tds[0].text
        star["link"] = 'https://baike.baidu.com' + all_tds[0].find('a').get('href')
        star["score"] = all_tds[1].text


        stars.append(star)

    json_data = json.loads(str(stars).replace("\'","\""))

    with open(today+'.json','w',encoding='UTF-8') as f:
        json.dump(json_data,f,ensure_ascii=False)




def crawl_pic_urls():

    with open(today+'.json','r',encoding='UTF-8') as file:
        json_array = json.loads(file.read())
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }

    for star in json_array:
        name = star['name']
        link = star['link']
        print(name)
        try:
            # 根据姓名查找图片连接
            response2 = requests.get(link, headers=headers)
            print(response2.status_code)
            soup = BeautifulSoup(response2.text, 'lxml')
            div = soup.find('div', {'class': 'summary-pic'})
            # 判断div是否为空，空表明没有图片链接
            # 没有这个判断碰到空对象则报错NoneType
            if div is None:
                continue
            pic_url = "https://baike.baidu.com"+ div.find('a').get('href')
            # 根据图片连接确定如片url列表
            response3 = requests.get(pic_url,headers=headers)
            print(response3.status_code)
            soup2 = BeautifulSoup(response3.text,'lxml')
            div2 = soup2.find('div',{'class':'pic-list'})
            # print(div2)
            img_list = div2.find_all('img')
            pic_urls = []  #pic_urls图片列表
            for item in img_list:
                # 将同一个人的照片url存储在列表中
                pic_urls.append(item.get('src'))

        except Exception as e:
            print(e)
        down_pic(name, pic_urls)

def down_pic(name, pic_urls):
    path = './pics/' + name + '/'
    if not os.path.exists(path):
        os.makedirs(path)
    for i, pic_url in enumerate(pic_urls):
        try:
            pic = requests.get(pic_url, timeout=15)
            string = str(i + 1) + '.jpg'
            with open(path + string, 'wb') as f:
                f.write(pic.content)
                print('成功下载第%s张图片： %s' % (str(i + 1), str(pic_url)))

        except Exception as e:
            print('下载第%s张图片时失败：%s' % (str(i + 1), str(pic_url)))
            print(e)
            continue

def show_pic_path(path):
    pic_num = 0
    for (dirpath,dirnames,filenames) in os.walk(path):
        for filename in filenames:
            pic_num += 1
            print("第%d张照片：%s" % (pic_num,os.path.join(dirpath,filename)))
    print("共爬取《青春有你2》选手的%d照片" % pic_num)


if __name__ == '__main__':
    html = crawl_wiki_data()
    parse_wiki_data(html)
    crawl_pic_urls()
    show_pic_path('./pics/')
    print("所有信息爬取完成！")