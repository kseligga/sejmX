from urllib.request import urlopen
import re

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

def cleanhtml(raw_html):
    nonums = re.sub('<td>.*?</td>', '', raw_html)
    withseparators=nonums.replace('</td>', '|')
    cleantext = re.sub('<.*?>', '', withseparators)
    voting_list = cleantext.split('|')
    votes = voting_list[1::2]
    mps = voting_list[::2]
    return mps, votes

def voting_result(html):
    tag_start = '<tbody>'
    tag_end = '</tbody>'

    start_index = html.find(tag_start) + len(tag_start)
    end_index = html.find(tag_end)

    mp_list = html[start_index:end_index]
    return cleanhtml(mp_list)


#print(voting_result(html))
print(voting_result(get_html(32,"PiS")))