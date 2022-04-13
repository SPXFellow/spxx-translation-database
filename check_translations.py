from jira import JIRA
from crowdin_api import CrowdinClient
import os, json

def get_translator(client, issue_id):
    res = client.source_strings.list_strings(4, filter=issue_id)
    if res['data']:
        target_id = res['data'][0]['data']['id']
        translation = client.string_translations.list_string_translations(projectId=4, stringId=target_id, languageId='zh-CN')
        if translation['data']:
            return translation['data'][0]['data']['user']['username']
        else:
            return ''
    else:
        return ''

class SPXCrowdinClient(CrowdinClient):
    TOKEN = os.getenv("CROWDIN_TOKEN")
    ORGANIZATION = "spx" # Optional, for Crowdin Enterprise only
    TIMEOUT = 60  # Optional, sets http request timeout.
    RETRY_DELAY = 0.1  # Optional, sets the delay between failed requests 
    MAX_RETRIES = 5  # Optional, sets the number of retries


if __name__ == "__main__":
    with open("translator.json", "r") as f:
        translator_info = json.load(f)
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

    with open("translator.json", "w") as f:
        json.dump(translator_info, f)

    #### Generate README here ####
    with open("README.md", "w") as f:
        rstr = "# SPXX Bug Translator Rank\n"
        rstr += '## Rank for Latest Version\n'
        def make_table(data: dict) -> str:
            header = "|Translator|Score|"
            spilter = "|---|---|"
            strs = [header, spilter]
            for tr, score in sorted([(tr, score) for tr, score in data.items()], key=lambda x: x[1], reverse=True):
                strs.append("|{}|{}|".format(tr, score))
            return '\n'.join(strs)
                
        rank = {}
        for issue in latest_fixed:
            key = issue.key
            if key in translator_info:
                translator = translator_info[key]
                rank[translator] = rank.get(translator, 0) + 1
        rstr += make_table(rank)
        rstr +='\n## Rank for All Time\nData since 22w14a.\n'
        rank = {}
        for key in translator_info:
            translator = translator_info[key]
            rank[translator] = rank.get(translator, 0) + 1
        rstr += make_table(rank)
        f.write(rstr)




