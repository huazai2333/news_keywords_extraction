import sys
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from keywords_generator import *
import collections

def getHTMLText(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()  # 如果状态不是200，引发HTTPError异常
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return "产生异常"


def get_oenday_ban_urls(year, mon, day):
    '''
       获取人民日报指定日期的所有版页面的url和版标题
       :param year: 要下载的年份
       :param mon:  要下载的月份
       :param day:  要下载的日
       :return: 记录每版url、版标题的列表。如
       [('http://paper.people.com.cn/rmrb/html/2021-01/20/nbs.D110000renmrb_01.htm',  '01版：要闻'),
        ('http://paper.people.com.cn/rmrb/html/2021-01/20/nbs.D110000renmrb_02.htm',  '02版：要闻'),
        ('http://paper.people.com.cn/rmrb/html/2021-01/20/nbs.D110000renmrb_03.htm',  '03版：要闻'),
        ...]
    '''

    url = 'http://paper.people.com.cn/rmrb/html/%4d-%02d/%02d/nbs.D110000renmrb_01.htm' % (year, mon, day)
    html = getHTMLText(url)
    soup = BeautifulSoup(html, 'lxml')
    links = soup.select("a#pageLink")
    ban_urls = []
    for link in links:
        pu = link['href']  # 得到 href 的值
        u = urljoin(url, pu)  # 将相对url转换为绝对url
        t = link.text.strip()  # 得到标签的文本
        ban_urls.append((u, t))
    return ban_urls


def get_oenban_article_urls(ban_url):
    '''
       获取一个版面的所有文章的链接信息
       :param ban_url: 版页面的url
       :return:记录当前版所有文章的url和标题的列表。如
   [ ('http://paper.people.com.cn/rmrb/html/2021-01/20/nw.D110000renmrb_20210120_1-12.htm', '情牵红寺堡，太多“没想到”（解码·脱贫之后探教育）  '),
    ('http://paper.people.com.cn/rmrb/html/2021-01/20/nw.D110000renmrb_20210120_2-12.htm', '年轻人爱上世界遗产（新语·让好声音成为最强音）  '),
   ...]
    '''
    html = getHTMLText(ban_url)
    soup = BeautifulSoup(html, 'lxml')
    links = soup.select("ul.news-list a")
    art_urls = []
    for link in links:
        pu = link['href']
        u = urljoin(ban_url, pu)
        t = link.text.strip()
        art_urls.append((u, t))
    return art_urls


def get_one_artcile_data(art_url):
    '''
       获取一篇文章的html，并解析出正文文本等数据
       :param art_url: 待下载文章的 url
       :return:
           当下载网页出错或无法解析网页时，返回 None
           当可以正常下载并解析网页时，返回：(text, introtitle, title, subtitle, author)
    '''
    html = getHTMLText(art_url)
    soup = BeautifulSoup(html, 'lxml')
    artb = soup.select_one('div.article')  # 获取包含文章信息的div块
    textb = artb.select_one('DIV#ozoom')  # 进一步得到包含正文文本的div块
    [s.extract() for s in textb('script')]  # 去掉块中的script块
    text = textb.get_text('\n').strip()  # 得到正文文本


    introtitle = artb.select_one('h3').text.strip()
    title = artb.select_one('h1').text.strip()
    subtitle = artb.select_one('h2').text.strip()
    # 下面获取作者信息
    conts = artb.select_one('p.sec').contents
    ss = ''
    for tag in conts:
        if tag.name == 'span' and tag.has_attr('class') and 'date' in tag.attrs['class']:
            break
        ss += tag.text
    author = ss.strip()


    return text, introtitle, title, subtitle, author

def download_one_day_people_daily(year, mon, day):
    '''
       下载指定日期人民日报的所有文章
       :param year: 年
       :param year: 月
       :param year: 日
       :return:
           当下载网页出错或无法解析网页时，返回 None
           当可以正常下载并解析网页时，返回：(text, introtitle, title, subtitle, author)
    '''
    sourlist = []
    ban_urls = get_oenday_ban_urls(2021, 1, 20)
    art_urls = []
    for ban_url, ban_title in ban_urls:
        ulist = get_oenban_article_urls(ban_url)
        for art_url, art_title, in ulist:
            art_urls.append((art_url, art_title, ban_title))

    for art_url, art_title, ban_title in art_urls:
        text, introtitle, title, subtitle, author = get_one_artcile_data(art_url)
        text = text.strip()
        sourlist.append(text)
        ban_id = ban_title.split('：')[0]
        # 分析地址后发现每个版面的文章数多少不一，最多有10（无法简单地提取字符串中的某一位），经过分析后发现每个url中最后一位'_'和'-'中间的部分即为文章编号，故采用rfind()提取art_index
        num_start = art_url.rfind('_')
        num_end = art_url.rfind('-')
        art_index = int(art_url[num_start + 1:num_end])
        if text != None:
            output_filename = '%4d%02d%02d-%s-%02d.txt' % (year, mon, day, ban_id, art_index)
        with open(output_filename, "wt", encoding='utf-8') as fw:
            if introtitle:
                fw.write(introtitle + '\n')  # 写入引标题
            fw.write(title + '\n')  # 写入标题
            if subtitle:
                fw.write(subtitle + '\n')  # 写入副标题
            if author:
                fw.write(author + '\n')  # 写入副标题
            fw.write('\n')  # 写入空行
            fw.write(text + '\n')  # 写入 text
        print('已写入文件：', output_filename)
    keywords = get_keywords(sourlist)
    print(keywords)


def main(args):
    download_one_day_people_daily(2021, 1, 20)

