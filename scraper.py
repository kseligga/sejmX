import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

term = 9

start_id_dict = {'7': 37494,
                 '8': 43801,
                 '9': 51988,
                 '10': 61401}
voting_nostart = start_id_dict[str(term)]
# TODO handle terms [3-6] (no nsf for them)


server_errors_counter=0
def get_html(voting_no, club_id):
    url = "https://www.sejm.gov.pl/sejm" + str(term) + ".nsf/agent.xsp?symbol=klubglos&IdGlosowania=" + \
          str(voting_nostart + voting_no) + \
          "&KodKlubu=" + club_id
    #print(voting_nostart + voting_no)

    while True:
        try:
            response = requests.get(url)
            response.raise_for_status()
            html = response.text
            return html
        except:
            print("Server error occurred (get_html)")
            global server_errors_counter
            server_errors_counter+=1
            continue



print("#####################################################################################################")


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
                vote = cols[2 + 3 * i].text.replace('Za', '1').replace('Przeciw', '-1') \
                    .replace('Wstrzymał się', '0').replace('Nieobecny', 'nan')
                votes_bin.append(int(vote) if vote != 'nan' else np.nan)
            except IndexError:
                pass

    dicts = {mps[i]: votes_bin[i] for i in range(len(mps))}
    return pd.DataFrame(dicts, index=[0])


clubs_url = "https://api.sejm.gov.pl/sejm/term" + str(term) + "/clubs"  # shouldn't use this
mps_url = "https://api.sejm.gov.pl/sejm/term" + str(term) + "/MP"

clubs = pd.read_json(clubs_url)
mps = pd.read_json(mps_url)

i = 1
count_none_streak = 0
votings = pd.DataFrame()
while True:
    votings_url = "https://api.sejm.gov.pl/sejm/term" + str(term) + "/votings/" + str(i)
    votings_sitting = pd.read_json(votings_url)
    if len(votings_sitting) > 0:
        votings = pd.concat([votings, votings_sitting])
        i += 1
        count_none_streak = 0
    else:
        count_none_streak += 1  # handling sittings without any votings
        if count_none_streak > 5:
            break
        i += 1

# we sort our votings to construct voting id number later on
votings.sort_values(['sitting', 'number'], ascending=[True, True], inplace=True)
votings = votings.reset_index()

# TRADITIONAL votings (id 53009 - 53024) - no data
print("total num of votings in term: " + str(len(votings)))

# list of indexes of proper votings
electronic_votings = votings.index[votings['kind'] == "ELECTRONIC"].tolist()  # TODO handle other votings
print("num of electronic votings in term: " + str(len(electronic_votings)))

#print(electronic_votings)
voting_df = pd.DataFrame(columns=(pd.Series(['voting_no'] + list(mps['lastFirstName']))))


def process_club(club):
    vres = voting_result(get_html(vote_n, club))
    vres['voting_no'] = vote_n
    return vres


def append_voting_df(vote_n, clubs):
    global voting_df

    with ThreadPoolExecutor() as executor:
        all_club_results = list(executor.map(process_club, clubs))

    all_club_results_df = pd.concat(all_club_results)
    cols_to_sum = all_club_results_df.columns.difference(['voting_no'])
    aggregated_results = all_club_results_df[cols_to_sum].sum(min_count=1).to_frame().T
    aggregated_results['voting_no'] = int(vote_n)
    voting_df = pd.concat([voting_df, aggregated_results])


#electronic_votings = electronic_votings[:100]


# print(electronic_votings)

def clubs_in_voting(sitting, number):
    url = "https://www.sejm.gov.pl/Sejm" + str(term) + ".nsf/agent.xsp?symbol=glosowania&NrKadencji=" + str(
        term) + "&NrPosiedzenia=" + str(sitting) + "&NrGlosowania=" + str(number)

    while True:
        try:
            response = requests.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            tbody = soup.find('tbody')
            rows = tbody.find_all('tr')

            clubs = [row.find('td').text for row in rows]  # optimizing code by list comprehension instead appends

            return clubs
        except:
            print("Server error occurred (clubs_in_voting)")
            global server_errors_counter
            server_errors_counter += 1
            continue

sittings = votings['sitting']  # optimizing code by searching only in necessary columns
numbers = votings['number']

for vote_n in electronic_votings:

    if vote_n % 100 == 0:
        print(vote_n)

    sitting = sittings.loc[vote_n]
    number = numbers.loc[vote_n]

    clubs = clubs_in_voting(sitting, number)
    append_voting_df(vote_n, clubs)

print('server errors: '+str(server_errors_counter))
voting_df.to_csv('voting_dfIX_full.csv')
print('all done')