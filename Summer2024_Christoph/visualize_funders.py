from pathlib import Path
from json import loads

from data_retrieval import get_review_meta_data

import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px 


if not Path("./reviews_with_meta_data.json").is_file():
    get_review_meta_data() 

# Structure:
# [{ 
#   "title": "abc", 
#   "doi": 123, 
#   "question": "abc?",
#   "references": [ 1, 2, 3 ] }, 
#   { ... }
# }]
with open("./reviews_with_meta_data.json") as file:
    reviews_with_meta_data = loads(file.read()) # 340 reviews; 16 with either broken DOIs or empty references

funders_df = pd.DataFrame(
    [funder for item in reviews_with_meta_data for funder in item['funders'] if funder.get("fundingBodyType", None) and funder.get("region", None)]
)

df = px.data.tips() 
  
fig = px.sunburst(funders_df, path=['fundingBodyType', 'region', 'name']) 
fig.show()
