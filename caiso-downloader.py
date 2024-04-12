# Import required packages
import argparse
from datetime import datetime, timedelta, date
import os
import glob
import pandas as pd
import csv
import time
import sys
import numpy as np
import json

# Parser setup
parser = argparse.ArgumentParser(prog='CAISO System Wide Demand and Supply Downloader',
                                 description='Downloads demand and supply data by reource type at 5-minute intervals',
                                 epilog='GNU Affero General Public License v3.0')

## Program argument validation
def valid_file_inputs(d):
    if d.endswith(".csv") == True:
        return d
    else:
        filename_error_message = "Not a valid filename input. Missing .csv extension."
        raise argparse.ArgumentTypeError(filename_error_message)

def valid_date_inputs(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        date_error_message = "Not a valid date input: {0!r}".format(s)
        raise argparse.ArgumentTypeError(date_error_message)

## Program arguments
parser.add_argument('filename',
                    type=valid_file_inputs,
                    help='The name of the output file with .csv extension (e.g. filename.csv)')
parser.add_argument('startdate',
                    type=valid_date_inputs, 
                    help='String input: YYYY-MM-DD')
parser.add_argument('enddate',
                    type=valid_date_inputs, 
                    help='String input: YYYY-MM-DD')
parser.add_argument('target',
                    choices=['all','demand','supply'],
                    help='Target data: all, demand, supply'
                    )

## Program argument 
args = parser.parse_args()

## Recieved program argument validation conditions
if args.startdate > args.enddate:
    print('Error: Provided start date exceeds the end date.')
    exit()
else:
    pass

if args.startdate < datetime.strptime('2018-04-10','%Y-%m-%d'):
    print('Error: Start date exceeds available data. Earliest available data is Apr 10, 2018.')
    exit()
else:
    pass

if args.enddate > (datetime.now() - timedelta(days=1)):
    print('Error: No data available for dates into the future. You entered:',args.enddate.strftime("%b %d%, %Y"))
    exit()
else:
    pass

input_delta = args.enddate - args.startdate

# File output location
results_location = os.path.join(sys.path[0], args.filename) # Operating system agnostic

# User argument summary
print(
    "Data source:", args.target, os.linesep,
    "Results location:", results_location, os.linesep,
    "Sample begins:", args.startdate.strftime("%b %d, %Y"), os.linesep,
    "Sample ends:", args.enddate.strftime("%b %d, %Y"), os.linesep,
    "Sample length:", (input_delta.days + 1), "days (", (input_delta.days + 1)*288, "observations )", os.linesep,
    "Downloading..."
)

# json object to easily add and remove working urls
urls_json = """
{
    "demand": "https://www.caiso.com/outlook/SP/History/datetime/demand.csv",
    "supply": "https://www.caiso.com/outlook/SP/History/datetime/fuelsource.csv"
}
"""

# URL Targets
if args.target == "supply":
    url = [json.loads(urls_json)['supply']]
if args.target == "demand":
    url = [json.loads(urls_json)['demand']]
if args.target == "all":
    url = [json.loads(urls_json)['supply'], json.loads(urls_json)['demand']]

# Initialize 
df_demand = pd.DataFrame()
df_supply = pd.DataFrame()

while args.startdate <= args.enddate:
    datetime = args.startdate.strftime('%Y%m%d')
    for i in range(len(url)):
        url_target = url[i].replace("datetime", datetime)
        tmp = pd.read_csv(url_target)
        tmp['Time'] = pd.to_datetime(args.startdate.strftime('%m/%d/%Y') + " " + tmp.iloc[:,0], format="%m/%d/%Y %H:%M")
        if i == 0:
            df_supply = pd.concat([df_supply, tmp], ignore_index=True)
        elif i == 1:
            df_demand = pd.concat([df_demand, tmp], ignore_index=True)
    args.startdate = args.startdate + timedelta(days=1)

# Collecting and exporting requested data
if args.target == 'all':
    df_demand = df_demand.set_index('Time')
    if df_demand.index.duplicated().any():
        df_demand_index_duplicated_values = df_demand[df_demand.index.duplicated()]
        with open('demand_error_log.txt', 'a') as f:
            df_demand_index_duplicated_values_str = df_demand_index_duplicated_values.to_string()
            f.write(df_demand_index_duplicated_values_str)
        print('Duplicate time values found in the demand data\nSee error log for removed observations details.\n First values kept.')
    df_demand = df_demand[~df_demand.index.duplicated(keep='first')]
    df_supply = df_supply.set_index('Time')
    if df_supply.index.duplicated().any():
        df_supply_index_duplicated_values = df_supply[df_supply.index.duplicated()]
        with open('supply_error_log.txt', 'a') as f:
            df_supply_index_duplicated_values_str = df_supply_index_duplicated_values.to_string()
            f.write(df_supply_index_duplicated_values_str)
        print('Duplicate time values found in the supply data\nSee error log for removed observations details.\n First values kept.')
    df_supply = df_supply[~df_supply.index.duplicated(keep='first')]
    df = pd.concat([df_demand, df_supply], axis=1)
    df.to_csv(results_location)
elif df_demand.empty:
    df_supply.to_csv(results_location,index=False)
elif df_supply.empty:
    df_demand.to_csv(results_location,index=False)

quit()
