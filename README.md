# Download System-wide CAISO Demand and Supply Data

This tool was designed to extract large time series from the [CAISO's Today's Outlook](https://www.caiso.com/TodaysOutlook/Pages/default.aspx) web service. This tool can download the following data in 15-minute intervals:

- Demand (MW)
    - Day ahead forecast, Hour ahead forecast, Current demand, Demand response (if available)
- Supply (MW)
    - Solar, Wind, Geothermal, Biomass, Biogas, Small Hydro, Coal,   Nuclear, Natural Gas, Large Hydro, Batteries, Imports, Other

This is a complete redesign of my [caiso-outlook-scraper](https://github.com/JesseKaczmarski/caiso-outlook-scraper). I used network analysis to identify URLs to call recursively instead of using Selenium for element-based webscraping. This halved the code base and removed Google browser and driver dependencies. It is also scalable to other sources on the [Today's Outlook](https://www.caiso.com/TodaysOutlook/Pages/default.aspx) which I will be adding at a later date (specifically resource adequacey). Enjoy!

# Installation

This is a script and should be run in a virtual environment. The script downloads the file to the directory it is run from. An example for setup is as follows,

1. Download the latest release and extract it to a folder of your choice.
2. Create a virtual enviornment in that directory location and install the requirements:
   * `$ python -m venv caiso`
   * `$ source caiso/bin/activate`, OS dependent. [See documentation](https://docs.python.org/3/library/venv.html#how-venvs-work) for your specific operating system.
   * `$ (caiso) pip install -r requirements.txt`
3. Once you have a working envrionment with the required packages, you may run the program as shown below.

# Usage

```
usage: 
    python caiso-downloader.py [-h] filename startdate enddate {all,demand,supply}

Downloads demand and supply data by reource type at 15-minute intervals

positional arguments:
  filename             Output path with .csv extension (e.g. filename.csv)
  startdate            String input: YYYY-MM-DD
  enddate              String input: YYYY-MM-DD
  {all,demand,supply}  Target data: all, demand, supply

options:
  -h, --help           show this help message and exit

```

# Example

```
(venv) $ python caiso-downloader.py supply-demand.csv 2021-01-01 2021-01-05 all

Data source: all 
 Results location: C:\projects\caiso-demand-supply-downloader\supply-demand.csv
 Sample begins: Jan 01, 2021
 Sample ends: Jan 05, 2021
 Sample length: 5 days ( 1440 observations )
Duplicate time values found in the demand data
See error log for removed observations details.
 First values kept.

```

Note: See [Disclaimer 2](#disclaimer-2) on duplicate time value warnings.

# Example Output

| Time          | Day ahead forecast | Hour ahead forecast | Current demand | Solar | Wind | Geothermal | Biomass | Biogas | Small hydro | Coal | Nuclear | Natural gas | Large hydro | Batteries | Imports | Other |
|---------------|--------------------|---------------------|----------------|-------|------|------------|---------|--------|-------------|------|---------|-------------|-------------|-----------|---------|-------|
| 1/1/2021 0:00 | 22662              | 21935               | 21937          | -41   | 1424 | 958        | 309     | 199    | 144         | 13   | 1144    | 8069        | 690         | -46       | 9541    | 0     |
| 1/1/2021 0:05 | 21434              | 21713               | 21858          | -41   | 1449 | 959        | 309     | 201    | 143         | 13   | 1145    | 8084        | 698         | -20       | 9388    | 0     |
| 1/1/2021 0:10 | 21434              | 21713               | 21827          | -41   | 1430 | 958        | 310     | 202    | 142         | 13   | 1145    | 8077        | 702         | 22        | 9314    | 0     |
| 1/1/2021 0:15 | 21434              | 21713               | 21757          | -41   | 1430 | 958        | 308     | 202    | 142         | 13   | 1145    | 8050        | 701         | 46        | 9247    | 0     |

### Disclaimer 1

The data from the CAISO is not perfect. There are bound to be several errors here and there. These errors would be present whether or not you downloaded the CSV files manually or through this program. 

### Disclaimer 2
By default, the program keeps the first occurance of duplicate time entries. Those duplicate entries and their data are output in an error log alongside the CSV.
