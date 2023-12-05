import csv
import json
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from scraper import voting_result, get_html

clubs_url = "https://api.sejm.gov.pl/sejm/term10/clubs"
mps_url = "https://api.sejm.gov.pl/sejm/term10/MP"
votings_url = "https://api.sejm.gov.pl/sejm/term10/votings/1"

clubs = pd.read_json(clubs_url)
mps = pd.read_json(mps_url)
votings = pd.read_json(votings_url)


firstday_clubs = ["PiS", "KO", "Polska2050", "PSL", "Nowa_Lewica", "Konfederacja"]
electronic_votings = votings.loc[votings['kind'] == "ELECTRONIC", 'number']


voting_df = pd.DataFrame(columns=(pd.Series(['voting_no'] + list(mps['lastFirstName']))))

print(voting_df.columns)
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

electronic_votings = electronic_votings[:20]
#print(electronic_votings)

for vote_n in electronic_votings:

    if vote_n < 8:
        append_voting_df(vote_n, firstday_clubs)
    else:
        append_voting_df(vote_n, clubs['id'])


print(voting_df)
#voting_df.to_csv('voting_dfX.csv')
