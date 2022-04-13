from jira import JIRA
from crowdin_api import CrowdinClient
import os, json

def get_translator(client, issue_id):
    res = client.source_strings.list_strings(4, filter=issue_id)
    if res['data']:
        target_id = res['data'][0]['data']['id']
        translation = client.string_translations.list_string_translations(projectId=4, stringId=target_id, languageId='zh-CN')
        return translation['data'][0]['data']['user']['username']
    else:
        return ''

class SPXCrowdinClient(CrowdinClient):
    TOKEN = os.getenv("CROWDIN_TOKEN")
    ORGANIZATION = "spx" # Optional, for Crowdin Enterprise only
    TIMEOUT = 60  # Optional, sets http request timeout.
    RETRY_DELAY = 0.1  # Optional, sets the delay between failed requests 
    MAX_RETRIES = 5  # Optional, sets the number of retries


if __name__ == "__main__":
    translator_info = json.load("translator.json")
    mojira = JIRA('https://bugs.mojang.com',auth=(os.getenv("JIRA_USERNAME"),os.getenv("JIRA_PASSWORD")))
    latest_fixed = mojira.search_issues('project = MC AND fixVersion = latestReleasedVersion()')
    future_fixed = mojira.search_issues('project = MC AND fixVersion = "Future Version - 1.19+"')
    client = SPXCrowdinClient()

    def query_translator(fixed):
        for issue in fixed:
            key = issue.key
            if key not in translator_info:
                translator = get_translator(client, key)
                if translator:
                    translator_info[key] = translator

    query_translator(latest_fixed)
    query_translator(future_fixed)

    json.dump("translator.json")


