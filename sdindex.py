import glob
import re
import os
import sys
from bs4 import BeautifulSoup


def to_dic(tag):
    # Create and return a dictionary with the <span> class value as key.
    # Put the value of the text of the direct child into the key 'text'.
    dic = {}
    for span in tag.find_all('span'):
        span_class = ' '.join(span['class'])
        span_text = ' '.join(span.stripped_strings)
        dic[span_class] = span_text.replace('\n', ' ')
    child_text = ' '.join([text.strip() for text in tag.find_all(
        string=True, recursive=False) if len(text.strip()) > 0])
    if child_text != '':
        dic['text'] = child_text
    return dic


def exec(filepath):
    with open(filepath, 'r') as file:
        data = file.read()

    soup = BeautifulSoup(data, 'html.parser')

    volume = soup.find(class_='mainTitleBook').string
    volume = re.sub(r'Software Design (\d{4})年(\d{1,2})月号', r'\1-0\2', volume)
    volume = re.sub(r'(\d{4}-)0(\d{2})', r'\1\2', volume)

    toc = soup.find(id='toc')

    latest_author = '-'
    order = 0
    for el in toc.find_all(['h3', 'li']):
        dic = to_dic(el)

        if 'author' in dic:
            dic['author'] = re.sub(r'^[…\s]+', '', dic['author'])

        if el.name == 'h3':
            latest_h3 = ''
            latest_h3 += ' ' + dic['text'] if 'text' in dic else ''
            latest_h3 += ' ' + dic['category'] if 'category' in dic else ''
            latest_h3 += ' ' + dic['title'] if 'title' in dic else ''
            latest_h3 += ' : ' + dic['catch'] if 'catch' in dic else ''
            latest_h3 = latest_h3.strip()

            if 'author' in dic:  # Sometimes the author is written in h3.
                latest_author = dic['author']
            else:
                latest_author = '-'

        else:  # li
            if len(dic) == 1 and 'author' in dic:
                latest_author = dic['author']
            else:
                order = order + 1

                if 'chapter' in dic:  # 特集
                    title = latest_h3
                    num = dic['chapter']
                    subtitle = re.sub(r'^：', '', dic['text'])
                    subtitle += ' : ' + re.sub(r'^：', '', dic['catch']) if 'catch' in dic else ''
                else:  # 一般記事, 連載
                    txt = ''
                    txt += ' ' + dic['text'] if 'text' in dic else ''
                    txt += ' ' + dic['title'] if 'title' in dic else ''
                    if 'catch' in dic:
                        if txt == '' or dic['catch'].startswith('【'):
                            txt += dic['catch']
                        else:
                            txt += ' : ' + re.sub(r'^：', '', dic['catch'])

                    result = re.match(r'(.+)【(\d+|.編|Part\d+)】(.+)', txt)
                    if result:
                        title = result.group(1).strip()
                        num = result.group(2).strip()
                        subtitle = result.group(3).strip()
                    else:
                        result = re.match(r'(.+) : (.+)', txt)
                        if result:
                            title = result.group(1).strip()
                            num = '-'
                            subtitle = result.group(2).strip()
                        else:
                            title = txt.strip()
                            num = '-'
                            subtitle = '-'

                    title = title.replace('【新連載】', '')
                    if '【最終回】' in title:
                        title = title.replace('【最終回】', '')
                        num += '(最終回)'

                if 'author' in dic:
                    author = dic['author']
                    latest_author = '-'
                else:
                    author = latest_author

                print_line(volume, str(order), title, num, subtitle, author)


def print_line(volume, order, title, num, subtitle, author):
    print('\t'.join([volume, str(order).zfill(2), title, num, subtitle, author]))


if __name__ == "__main__":
    print('\t'.join(['volume', 'order', 'title', 'num', 'subtitle', 'author']))
    files = sorted(glob.glob(sys.argv[1] + '/*'))
    for file in files:
        exec(file)
