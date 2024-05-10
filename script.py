from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import sys
from pyquery import PyQuery as pq
import pandas as pd
import numpy as np
from datetime import datetime
from selenium.common.exceptions import WebDriverException
import time
import os
import re
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

MAX_LINKS = 50

dfs = []
rows = []

class game_row:
    def __init__(self, url, team):
        self.url = url
        self.team = team
    
class stats_guy:
    def __init__(self, sdql):
        chrome_service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--log-level=3")
        self.driver = webdriver.Chrome(service=chrome_service, options=options)
        self.sdql = sdql + " and date < " + datetime.now().date().strftime("%Y%m%d")
        self.html = ""

    def __del__(self):
        self.driver.quit()

    def get_html(self, url):
        retries = 3
        while retries > 0:
            try:
                print("get: ", url)
                self.driver.get(url)
                return self.driver.page_source
            except Exception as e:
                retries -= 1
                print(f"Error occurred while fetching HTML for url: {url}")
                print(f"Exception: {e}")
                if retries == 0:
                    print(f"Maximum retries reached for url: {url}")
                    print()
                    return None

    def get_killersports_html(self):
        return self.get_html(
            "https://killersports.com/nba/query?_qt=games&sdql=" + self.sdql
        )

    def get_killersports_links(self):
        doc = pq(self.get_killersports_html())
        table = doc("#DT_Table")
        results_length = len(list(table("tbody tr").items()))

        for row in table("tbody tr").items():
            link = row('td').eq(1)('a').attr('href')
            link = link.replace("UTH", "UTA")
            t1 = row('td').eq(4).text()
            rows.append(game_row(link, t1))

        if results_length == MAX_LINKS:
            earliest_date = table("tbody tr > td").eq(0).text()
            date_object = datetime.strptime(earliest_date, "%b %d, %Y")
            formatted_date = date_object.strftime("%Y%m%d")
            self.sdql += " and date <= " + formatted_date
            self.get_killersports_links()

    def get_player_stats(self):
        columns = [
            "Player",
            "MP",
            "FG",
            "FGA",
            "FG_PCT",
            "FG3",
            "FG3A",
            "FG3_PCT",
            "FT",
            "FTA",
            "FT_PCT",
            "ORB",
            "DRB",
            "TRB",
            "AST",
            "STL",
            "BLK",
            "TOV",
            "PF",
            "PTS",
            "PLUS_MINUS",
            "G",
        ]
        data = pd.DataFrame(columns=columns)
        data = []
        for row in rows:
            link = row.url
            pattern = r"\/boxscores\/(.+)\.html"
            match = re.search(pattern, link)
            file_path = os.path.join("data", match.group(1))
            print(file_path)
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as file:
                    html = file.read()
            else:
                time.sleep(3)
                html = self.get_html(link)
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(html)

            if html:
                doc = pq(html)
                tables = doc("table[id*=box][id*=game-basic]")
                
                table1_team = tables('caption').eq(0).text()
                table2_team = tables('caption').eq(1).text()

                table = None

                if row.team in table1_team:
                    table = tables.eq(0)
                elif row.team in table2_team:
                    table = tables.eq(1)

                for row in table("tbody tr").items():
                    player_name = row('th[data-stat="player"] a').text()
                    if not player_name:
                        continue
                    mp_value = row('td[data-stat="mp"]').text()
                    mp_minutes = mp_value.split(":")[0]

                    if not mp_minutes:
                        continue

                    mp_total_minutes = int(mp_minutes)
                    player_exists = [
                        player for player in data if player["Player"] == player_name
                    ]

                    if player_exists:
                        player = player_exists[0]
                        for idx, val in enumerate(row("td").items(), start=1):
                            if columns[idx] == "MP":
                                player["MP"] += mp_total_minutes
                            else:
                                try:
                                    val_text = val.text()
                                    if val_text:
                                        if columns[idx] == "FG_PCT":
                                            if player["FG"] == 0:
                                                player[columns[idx]] = 0
                                            else:
                                                player[columns[idx]] = round(
                                                    player["FG"] / player["FGA"], 2
                                                )
                                        elif columns[idx] == "FG3_PCT":
                                            if player["FG3"] == 0:
                                                player[columns[idx]] = 0
                                            else:
                                                player[columns[idx]] = round(
                                                    player["FG3"] / player["FG3A"], 2
                                                )
                                        elif columns[idx] == "FT_PCT":
                                            if player["FT"] == 0:
                                                player[columns[idx]] = 0
                                            else:
                                                player[columns[idx]] = round(
                                                    player["FT"] / player["FTA"], 2
                                                )
                                        else:
                                            player[columns[idx]] += int(val_text)
                                    else:
                                        player[columns[idx]] += 0
                                except Exception as e:
                                    print()
                                    print(e)
                                    print()
                                    print(link)
                                    print()
                                    print(player, val_text, idx, columns[idx])
                                    print()
                                    for idx, val in enumerate(row("td").items()):
                                        print(idx, val)
                                    exit()
                        player["G"] += 1
                    else:
                        new_player = {"Player": player_name, "MP": mp_total_minutes}
                        for idx, val in enumerate(row("td").items(), start=1):
                            if columns[idx] == "MP":
                                continue
                            else:
                                try:
                                    val_text = val.text()
                                    if val_text:
                                        if columns[idx] == "FG_PCT":
                                            if new_player["FG"] == 0:
                                                new_player[columns[idx]] = 0
                                            else:
                                                new_player[columns[idx]] = round(
                                                    new_player["FG"]
                                                    / new_player["FGA"],
                                                    2,
                                                )
                                        elif columns[idx] == "FG3_PCT":
                                            if new_player["FG3"] == 0:
                                                new_player[columns[idx]] = 0
                                            else:
                                                new_player[columns[idx]] = round(
                                                    new_player["FG3"]
                                                    / new_player["FG3A"],
                                                    2,
                                                )
                                        elif columns[idx] == "FT_PCT":
                                            if new_player["FT"] == 0:
                                                new_player[columns[idx]] = 0
                                            else:
                                                new_player[columns[idx]] = round(
                                                    new_player["FT"]
                                                    / new_player["FTA"],
                                                    2,
                                                )
                                        else:
                                            new_player[columns[idx]] = int(val_text)
                                    else:
                                        new_player[columns[idx]] = 0
                                except Exception as a:
                                    print(new_player)
                                    print()
                                    print(a)
                                    exit()

                        new_player["G"] = 1
                        data.append(new_player)

        data = pd.DataFrame(data)
        data.insert(1, "BPM", round(data["PLUS_MINUS"] / data["G"], 2))
        data.insert(1, "BPG", round(data["BLK"] / data["G"], 2))
        data.insert(1, "SPG", round(data["STL"] / data["G"], 2))
        data.insert(1, "APG", round(data["AST"] / data["G"], 2))
        data.insert(1, "RPG", round(data["TRB"] / data["G"], 2))
        data.insert(1, "3PA", round(data["FG3A"] / data["G"], 2))
        data.insert(1, "3P", round(data["FG3"] / data["G"], 2))
        data.insert(1, "PPG", round(data["PTS"] / data["G"], 2))
        data.insert(1, "MPG", round(data["MP"] / data["G"], 2))
        data.insert(1, "FGM", round(data["FG"] / data["G"], 2))
        data.insert(1, "FGATT", round(data["FGA"] / data["G"], 2))
        data.insert(1, "FTM", round(data["FT"] / data["G"], 2))
        data.insert(1, "FTATT", round(data["FTA"] / data["G"], 2))
        data.insert(1, "TPG", round(data["TOV"] / data["G"], 2))
        data.insert(1, "FPG", round(data["PF"] / data["G"], 2))
        data.insert(
            1,
            "P + R + A",
            round(
                round(data["PTS"] / data["G"], 2)
                + round(data["TRB"] / data["G"], 2)
                + round(data["AST"] / data["G"], 2),
                2,
            ),
        )

        data = data[
            [
                "Player",
                "MP",
                "G",
                "MPG",
                "PPG",
                "RPG",
                "APG",
                "P + R + A",
                "3P",
                "FGM",
                "FGATT",
                "FG_PCT",
                "3PA",
                "FG3_PCT",
                "FTM",
                "FTATT",
                "FT_PCT",
                "SPG",
                "BPG",
                "TPG",
                "FPG",
                "BPM",
            ]
        ]

        data_sorted = data.sort_values(by="MP", ascending=False)
        data_sorted.to_csv(
            "C:\\Users\\GiulianTrabucco\\OneDrive - Buyers Edge Platform\\Desktop\\player-stats\\results.txt",
            sep="\t",
            index=False,
        )

    def run(self):
        self.get_killersports_links()
        self.get_player_stats()

sg = stats_guy(sys.argv[1])
sg.run()