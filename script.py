from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import sys
from pyquery import PyQuery as pq
import pandas as pd
import numpy as np


class stats_guy:
    def __init__(self, sdql):
        chrome_service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(service=chrome_service, options=options)
        self.sdql = sdql

    def __del__(self):
        self.driver.quit()

    def get_html(self, url):
        self.driver.get(url)
        html = self.driver.page_source
        return html

    def get_killersports_html(self):
        html = self.get_html(
            "https://killersports.com/nba/query?_qt=games&sdql=" + self.sdql
        )
        return html

    def get_killersports_links(self, html):
        doc = pq(html)
        table = doc("#DT_Table")
        anchor_tags = table.find("a")
        anchor_values = [a.attrib["href"] for a in anchor_tags]
        return anchor_values

    def get_player_stats(self, links):
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
        for link in links:
            html = self.get_html(link)
            doc = pq(html)
            tables = doc("table[id*=box][id*=game-basic]")
            for row in tables("tbody tr").items():
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
                                                new_player["FG"] / new_player["FGA"], 2
                                            )
                                    elif columns[idx] == "FG3_PCT":
                                        if new_player["FG3"] == 0:
                                            new_player[columns[idx]] = 0
                                        else:
                                            new_player[columns[idx]] = round(
                                                new_player["FG3"] / new_player["FG3A"],
                                                2,
                                            )
                                    elif columns[idx] == "FT_PCT":
                                        if new_player["FT"] == 0:
                                            new_player[columns[idx]] = 0
                                        else:
                                            new_player[columns[idx]] = round(
                                                new_player["FT"] / new_player["FTA"], 2
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

        data.insert(1, "BPG", round(data["BLK"] / data["G"], 2))
        data.insert(1, "SPG", round(data["STL"] / data["G"], 2))
        data.insert(1, "APG", round(data["AST"] / data["G"], 2))
        data.insert(1, "RPG", round(data["TRB"] / data["G"], 2))
        data.insert(1, "3PA", round(data["FG3A"] / data["G"], 2))
        data.insert(1, "3P", round(data["FG3"] / data["G"], 2))
        data.insert(1, "PPG", round(data["PTS"] / data["G"], 2))
        data.insert(1, "MPG", round(data["MP"] / data["G"], 2))

        data_sorted = data.sort_values(by="MP", ascending=False)
        data_sorted.to_csv(
            "C:\\Users\\giuli\\Desktop\\player-stats\\results.txt",
            sep="\t",
            index=False,
        )


sg = stats_guy(sys.argv[1])
html = sg.get_killersports_html()
links = sg.get_killersports_links(html)
stats = sg.get_player_stats(links)
