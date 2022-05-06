import io
import re

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from scipy.spatial import distance
from selenium import webdriver
import pdftotext

V_GENE_PREFIX = 'IGHV'
J_GENE_PREFIX = 'IGHJ'


def search():
    # setup Driver|Chrome : 크롬드라이버를 사용하는 driver 생성
    driver = webdriver.Chrome('./chromedriver')
    v_gene = V_GENE_PREFIX + '4-59'
    j_gene = J_GENE_PREFIX + '3'
    cdr3_sequence = 'ARDSYCSGGSCFDWYFDL'

    hamming_limit = 0.3

    # v_gene = input("V-gene? (Enter 's' for skip.)")
    # j_gene = input("J-gene? (Enter 's' for skip.)")
    # cdr3_sequence = input("CDR3 Sequence? (Enter 's' for skip.)")

    # v_gene = None if v_gene == 's' else V_GENE_PREFIX + v_gene
    # j_gene = None if j_gene == 's' else J_GENE_PREFIX + j_gene
    # cdr3_sequence = None if cdr3_sequence == 's' else cdr3_sequence

    keyword = get_keyword(v_gene, j_gene)
    # keyword = '"IGHV4-59" AND "IGHJ3"'
    # keyword = 'V4-59+ARDSYCSGGSCFDWYFDL'

    if keyword is None:
        print('')
        print('No keyword entered.')
        return

    print('')
    print('Search with keyword : ' + keyword)

    driver.get('https://google.com/search?q=' + keyword)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    r = soup.select('.yuRUbf')

    result_list = []

    for i in r:
        print()
        title = i.select_one('.LC20lb.MBeuO.DKV0Md').text
        href = i.a.attrs['href']
        print(href)

        if cdr3_sequence is not None:
            response = requests.get(href)
            content_type = response.headers["Content-Type"]

            print("content Type = " + requests.get(href).headers["Content-Type"])

            if "pdf" in content_type:
                data = get_pdf_text(response)
                print("Data = " + data)
            else:
                driver.get(href)
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')

                length = cdr3_sequence.__len__()
                regex = get_length_regex_pattern(length)
                target = np.array(list(cdr3_sequence))
                result = soup.findAll(text=re.compile(regex))

                count = 0
                hit = list()
                for item in result:
                    sub_result = re.findall(regex, item)
                    for subItem in sub_result:
                        sub_array = np.array(list(subItem))
                        sub_d = distance.hamming(sub_array, target)

                        if sub_d <= hamming_limit:
                            count = count + 1
                            hit.append(subItem)
                            print("hit added : " + subItem + ", d : " + str(sub_d))

                print('hit count = ' + str(count))
                result_str = [title, href, count]


        else:
            result_str = [title, href, 0]
            # print()
            # for item in result:
            #     print(item)
            #     print(item.findParent().text[:100]
            #     print()

        result_list.append(result_str)

    result_df = pd.DataFrame(result_list, columns=['Title', 'Link', 'Hit Count'])
    result_df.to_csv(f'result_list.csv', mode='w', encoding='utf-8-sig', header=True, index=True)

    driver.close()


def get_keyword(v_gene, j_gene):
    if v_gene is None and j_gene is None:
        return None
    elif j_gene is None:
        return '\"' + v_gene + '\"'
    elif v_gene is None:
        return '\"' + j_gene + '\"'
    else:
        return '\"' + v_gene + '\"+AND+\"' + j_gene + '\"'


def get_length_regex_pattern(length):
    return "\\b\\w{" + str(length) + "}\\b"


def get_pdf_text(response):
    stream = io.BytesIO(response.content)
    reader = PyPDF4.PdfFileReader(stream)

    text = u""

    if reader.getDocumentInfo().title:
        # Title is optional, may be None
        text += reader.getDocumentInfo().title

    for page in reader.pages:
        # XXX: Does handle unicode properly?
        text += page.extractText()

    return text
00º

def read_pdf(url):
    response = requests.get(url)
    content_type = response.headers["Content-Type"]

    print("content Type = " + content_type)

    if "pdf" in content_type:
        data = get_pdf_text(response)
        print("Data = " + data)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # search()
    read_pdf("https://www.jimmunol.org/content/192/10/4551.full.pdf?with-ds=yes")





# See PyCharm help at https://www.jetbrains.com/help/pycharm/
