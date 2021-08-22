# -*- coding:utf-8 -*-
import os
import bs4
import requests
import time
import datetime
import sys
import pandas as pd
from PyPDF2 import PdfFileMerger
import warnings
warnings.filterwarnings("ignore")
# PyPDF2在合并时有未知bug，不断抛出告警。然而，合并的PDF并没有问题，故为方便使用，关闭告警提示


class Paper:
    def __init__(self, date):
        # os.chdir('..')
        if 'temp' not in os.listdir():
            os.mkdir('./temp')
        self.date_str = date
        self.fmt = '%Y%m%d'
        time_tuple = time.strptime(self.date_str, self.fmt)
        self.year, self.month, self.day = time_tuple[:3]
        self.date = datetime.date(self.year, self.month, self.day)
        self.headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image   /webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 Edg/88.0.705.68'}
        self.url = 'http://paper.people.com.cn/rmrb/'
        self.page_titles = []
        self.pdf_files = []

    def fetch_page_title(self):
        url = self.url + 'html/' + self.date.strftime("%Y-%m/%d/") + 'nbs.D110000renmrb_01.htm'
        # print("url:", url)
        r = requests.get(url, headers=self.headers)
        r.raise_for_status()
        r.encoding = 'utf-8'
        html = r.text
        bsobj = bs4.BeautifulSoup(html, 'html.parser')
        page_lists = bsobj.find_all('div', attrs={'class': 'swiper-slide'})
        for page in page_lists:
            self.page_titles.append(page.text)

    def get_single_pdf(self):
        url = self.url + 'images/'
        page_number = len(self.page_titles)
        for page in range(1, page_number+1):
            page = str(page).zfill(2)
            file_name = page + '.pdf'
            page_url = url + self.date.strftime('%Y-%m/%d/') + page + self.date.strftime('/rmrb%Y%m%d') + file_name
            # print("page_url:", page_url)
            self.pdf_files.append(file_name)
            html_str = requests.get(page_url, headers=self.headers).content
            file_name = './temp/' + file_name
            with open(file_name, 'wb') as f:
                f.write(html_str)
            # time.sleep(0.2)

    def merge_pdf(self):
        os.chdir('./temp')
        merge_name = self.date.strftime('%Y%m%d') + '.pdf'
        pdf_num = len(self.pdf_files)
        pdf_merger = PdfFileMerger(strict=False)
        for i in range(pdf_num):
            pdf_merger.append(self.pdf_files[i])
            pdf_merger.addBookmark(title=self.page_titles[i], pagenum=i)
        os.chdir('..')
        os.chdir('./'+str(self.year))
        with open(merge_name, 'wb') as f:
            pdf_merger.write(f)
        del pdf_merger
        os.chdir('..')

    def is_exist(self):
        if str(self.year) not in os.listdir():
            os.mkdir('./'+str(self.year))
        os.chdir('./'+str(self.year))
        file_name = str(self.year)+str(self.month).zfill(2)+str(self.day).zfill(2)+'.pdf'
        if file_name in os.listdir():
            os.chdir('..')
            return True
        else:
            os.chdir('..')
            return False

    def get_paper(self):
        file_name = str(self.year)+str(self.month).zfill(2)+str(self.day).zfill(2)+'.pdf'
        if not self.is_exist():
            print("Download:" + file_name)
            self.fetch_page_title()
            self.get_single_pdf()
            self.merge_pdf()
            print("Complete:" + file_name)
        else:
            print('Exist:' + file_name)


def main():
    begin_date = datetime.date.today().strftime('%Y%m%d')
    if len(sys.argv) >= 2:
        begin_date = sys.argv[1]
    end_date = begin_date
    if len(sys.argv) >= 3:
        end_date = sys.argv[2]
    date_list = [datetime.datetime.strftime(x, '%Y%m%d') for x in list(pd.date_range(start=begin_date, end=end_date))]
    for date in date_list:
        p = Paper(date)
        p.get_paper()


if __name__ == '__main__':
    main()
