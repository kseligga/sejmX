from urllib.request import urlopen
import re

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

voting_no=2
voting_nostart=61400
club_id = 'PiS'

def get_html(voting_no, club_id):
    url = "https://www.sejm.gov.pl/sejm10.nsf/agent.xsp?symbol=klubglos&IdGlosowania=" + \
          str(voting_nostart + voting_no) + \
          "&KodKlubu=" + club_id

    page = urlopen(url)
    html_bytes = page.read()
    html = str(html_bytes.decode("utf-8"))
    if html[1]=="h":
        return ""
    return html

#
# f=open('urltext.txt', 'w+')
# f.write(html)

f=open('urltext.txt',"r+")
html=f.read()

print("#####################################################################################################")



# def voting_result(html):
#     tag_start = '<tbody>'
#     tag_end = '</tbody>'
#
#     start_index = html.find(tag_start) + len(tag_start)
#     end_index = html.find(tag_end)
#
#     mp_list = html[start_index:end_index]
#
#     def cleanhtml(raw_html):
#         nonums = re.sub('<td>.*?</td>', '', raw_html)
#         withseparators = nonums.replace('</td>', '|')
#         cleantext = re.sub('<.*?>', '', withseparators)
#
#         voting_list = cleantext.split('|')
#
#         votes = voting_list[1::2]
#         mps = voting_list[::2]
#
#         votes = list(filter(None, votes))
#         mps = list(filter(None, mps))
#         return mps, votes
#
#     mps, votes = cleanhtml(mp_list)
#     votes_bin = list(map(lambda x: x.replace('Za','1').replace('Przeciw','-1').replace('Wstrzymał się','0').replace('Nieobecny','nan'), votes))
#     votes_bin = list(map(lambda x: int(x) if x != 'nan' else np.nan, votes_bin))
#
#     dicts = {mps[i]: votes_bin[i] for i in range(len(mps))}
#     return pd.DataFrame(dicts, index=[0])

def voting_result(html):
    soup = BeautifulSoup(html, 'html.parser')
    tbody = soup.find('tbody')
    rows = tbody.find_all('tr')

    mps = []
    votes_bin = []


    for row in rows:
        cols = row.find_all('td')
        for i in range(2):
            try:
                mps.append(cols[1 + 3 * i].text)
                vote = cols[2 + 3 * i].text.replace('Za', '1').replace('Przeciw', '-1').replace('Wstrzymał się',
                                                                                                '0').replace(
                    'Nieobecny', 'nan')
                votes_bin.append(int(vote) if vote != 'nan' else np.nan)
            except IndexError:
                pass


    dicts = {mps[i]: votes_bin[i] for i in range(len(mps))}
    return pd.DataFrame(dicts, index=[0])

#print(voting_result(html))
#print(voting_result(get_html(8,"PSL")))