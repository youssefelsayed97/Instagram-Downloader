import json
import re
import pyshorteners
import pandas as pd
from tabulate import tabulate


class Scraper:

    def __init__(self, loader):
        self.loader = loader

        self.headers = {
            "X-IG-App-ID": "936619743392459",
            "X-Requested-With": "XMLHttpRequest",
        }

    @property
    def session(self):
        return self.loader.context._session


    def mutual_followers(self, user_id):
        url = f"https://www.instagram.com/api/v1/friendships/{user_id}/mutual_followers/"
        response = self.session.get(url, params={"page_size": 12}, headers = self.headers)
        if response.status_code == 200:
            # print(response.status_code)
            data = response.json()
            usernames = [user["username"] for user in data["users"]]
            return usernames
        else:
            # print(response.status_code)
            return []


    def get_fb_dtsg_token(self):

        response = self.session.get("https://www.instagram.com/explore/search/", headers = self.headers)

        match = re.search(r'"DTSGInitialData",\[\],\{"token":"([^"]+)"\}', response.text)

        if match:
            token = match.group(1)
            return token
        else:
            return None


    def search_account(self, search_query):

        fb_dtsg = self.get_fb_dtsg_token()

        if fb_dtsg is None:
            print("could not scrape fb_dtsg token")
            return


        url = "https://www.instagram.com/api/graphql"

        variables = {
            "data": {
                # "context": "blended",
                # "include_reel": "true",
                "query": search_query,
                # "rank_token": "",
                # "search_session_id": "",
                # "search_surface": "web_top_search"
            },
            "hasQuery": True,
            "__relay_internal__pv__PolarisAIGMAccountLabelEnabledrelayprovider": False
        }

        # print(json.dumps(variables))

        payload = {
            "fb_dtsg": fb_dtsg,
            "variables": json.dumps(variables),
            "doc_id": "26841114978842944" # doc_id source is PolarisSearchBoxRefetchableQuery_instagramRelayOperation
        }

        headers = {
            'accept': '*/*',
            'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8,de-DE;q=0.7,de;q=0.6',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.instagram.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.instagram.com/explore/search/',
            'sec-ch-prefers-color-scheme': 'dark',
            'sec-ch-ua': '"Not;A=Brand";v="8", "Chromium";v="150", "Microsoft Edge";v="150"',
            'sec-ch-ua-full-version-list': '"Not;A=Brand";v="8.0.0.0", "Chromium";v="150.0.7871.115", "Microsoft Edge";v="150.0.4078.65"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"19.0.0"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0',
            'x-asbd-id': '359341',
            }

        response = self.session.post(url, headers=headers, data=payload)

        if response.status_code == 200:

            data = response.json()
            results = []
            s = pyshorteners.Shortener()
            counter = 0
            for counter, user in enumerate(data["data"]["xdt_api__v1__fbsearch__topsearch_connection"]["users"]):
                data = {
                        # "no.": user["position"] + 1,
                        "no.": counter +1,
                        "id": user["user"]["pk"],
                        "username": user["user"]["username"],
                        "is_verified": user["user"]["is_verified"],
                        "name": user["user"]["full_name"],
                        "profile_image_url": s.tinyurl.short(user["user"]["hd_profile_pic_url_info"]["url"]),
                }
                results.append(data)

            # total_results = len(results)
            if results:
                total_results = counter + 1
                results = json.dumps(results, indent=4)
                print("Total results: ", total_results)

                df = pd.DataFrame(json.loads(results))
            # df["profile_image_url"] = df["profile_image_url"].str.slice(0, 40) + "..."


                print(tabulate(df, headers="keys", tablefmt="grid", showindex=False))
            else:
                print("No results found.")
        else:
            return None



