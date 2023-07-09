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
        text=True, recursive=False) if len(text.strip()) > 0])
    if child_text != '':
        dic['text'] = child_text
    return dic


def exec(filepath):
    with open(filepath, 'r') as file:
        data = file.read()

    soup = BeautifulSoup(data, 'html.parser')

    volume = soup.find(class_='mainTitleBook').string
    volume = volume.replace('Software Design ', '')
    if re.match(r'\d{4}年\d月号', volume):
        volume = volume.replace('年', '年0')

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
    print('      <tr><td>' + volume + '</td><td>' + str(order).zfill(2) + '</td><td>' + title +
          '</td><td>' + num + '</td><td>' + subtitle + '</td><td>' + author + '</td></tr>')


def print_head(eldest, latest):
    template = '''
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>Software Design {eldest}～{latest} 総目次</title>
    <style>
      button {
        margin: 0 0 1em 0.5em;
      }
      table {
        border-collapse: collapse;
      }
      th {
        color: white;
        background: navy;
        cursor: pointer;
        white-space: nowrap;
      }
      th.sort-asc::after {
        content: '↓';
      }
      th.sort-desc::after {
        content: '↑';
      }
      td {
        padding: 0 0.3em;
        border-bottom: 1px solid lightgray;
        vertical-align: top;
      }
      td:nth-child(1) {
        white-space: nowrap;
      }
      td:nth-child(4) {
        min-width: 4em;
      }
    </style>

    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-FJ6KMH2L76"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());

      gtag('config', 'G-FJ6KMH2L76');
    </script>
  </head>

  <body>
    <h1>Software Design {eldest}～{latest} 総目次</h1>
    <table>
      <tr><th>号</th><th>目次順</th><th>タイトル</th><th>回</th><th>サブタイトル</th><th>著者</th></tr>
        '''.strip()
    print(template.replace('{eldest}', eldest).replace('{latest}', latest))


def print_tail():
    print('''
    </table>

    <script>
      initialize();

      function initialize() {
        const body = document.querySelector('body');
        const table = document.querySelector('table');

        const input = document.createElement('input');
        input.addEventListener('keypress', () => {
          if (event.key === 'Enter') filterRows();
        });
        body.insertBefore(input, table);

        const button = document.createElement('button');
        button.textContent = '正規表現で検索';
        button.onclick = filterRows;
        body.insertBefore(button, table);

        document.querySelectorAll('th').forEach(th => th.onclick = sortRows);
        document.querySelector('th').classList.add('sort-asc');
      }

      function filterRows() {
        const keyword = document.querySelector('input').value;
        const regex = new RegExp(keyword, 'i');
        const table = document.querySelector('table');
        for (let i = 1; i < table.rows.length; i++) {
          const row = table.rows[i];
          row.style.display = 'none';
          for (let j = 0; j < row.cells.length; j++) {
            if (row.cells[j].textContent.match(regex)) {
              row.style.display = 'table-row';
              break;
            }
          }
        }
      }

      function sortRows() {
        const table = document.querySelector("table");
        const records = [];
        for (let i = 1; i < table.rows.length; i++) {
          const record = {};
          record.row = table.rows[i];
          record.key = table.rows[i].cells[this.cellIndex].textContent;
          records.push(record);
        }
        if (this.classList.contains('sort-asc')) {
          records.sort(compareKeysReverse);
          purgeSortMarker();
          this.classList.add('sort-desc');
        } else {
          records.sort(compareKeys);
          purgeSortMarker();
          this.classList.add('sort-asc');
        }
        for (let i = 0; i < records.length; i++) {
          table.appendChild(records[i].row);
        }
      }

      function purgeSortMarker() {
        document.querySelectorAll('th').forEach(th => {
          th.classList.remove('sort-asc');
          th.classList.remove('sort-desc');
        });
      }

      function compareKeys(a, b) {
        if (a.key < b.key) return -1;
        if (a.key > b.key) return 1;
        return 0;
      }

      function compareKeysReverse(a, b) {
        if (a.key < b.key) return 1;
        if (a.key > b.key) return -1;
        return 0;
      }
    </script>
  </body>
</html>
    '''.strip())

if __name__ == "__main__":
    files = sorted(glob.glob(sys.argv[1] + '/*'))
    eldest = re.sub(r'.*(\d{4})(\d{2})\.htm', r'\1.\2', files[0])
    latest = re.sub(r'.*(\d{4})(\d{2})\.htm', r'\1.\2', files[-1])

    print_head(eldest, latest)
    for file in files:
        exec(file)
    print_tail()
