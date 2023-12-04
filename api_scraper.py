import json

import pandas as pd
import requests

clubs_url = "https://api.sejm.gov.pl/sejm/term10/clubs"

kluby = pd.read_json(clubs_url)

print(kluby['id'])