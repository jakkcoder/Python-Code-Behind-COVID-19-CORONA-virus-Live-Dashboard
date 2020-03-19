
## Get corona data api

def get_corona_data():
    from bs4 import BeautifulSoup
    import requests
    import pandas
    url="https://www.worldometers.info/coronavirus/"
    # Make a GET request to fetch the raw HTML content
    html_content = requests.get(url).text
    # Parse the html content
    soup = BeautifulSoup(html_content, "lxml")
    gdp_table = soup.find("table", id = "main_table_countries")
    gdp_table_data = gdp_table.tbody.find_all("tr")

    # Getting all countries names
    dicts = {}
    for i in range(len(gdp_table_data)):
        try:
            key = (gdp_table_data[i].find_all('a', href=True)[0].string)
        except:
            key = (gdp_table_data[i].find_all('td')[0].string)

        value = [j.string for j in gdp_table_data[i].find_all('td')]
        dicts[key] = value
    live_data= pd.DataFrame(dicts).drop(0).T
    live_data.columns = ["TotalCases", "New Cases","Total Deaths", "New Deaths", "Total Recovered","Active","Serious Critical",
"Tot Cases/1M pop"]
    
    return(live_data)

