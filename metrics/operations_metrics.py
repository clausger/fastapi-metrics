from github import Github
import os, statistics, datetime

TOKEN  = os.getenv("GITHUB_TOKEN")
REPO   = "tiangolo/fastapi"
WINDOW = 365  # días

gh = Github(TOKEN)
repo = gh.get_repo(REPO)
since = datetime.datetime.utcnow() - datetime.timedelta(days=WINDOW)

dur = [(i.closed_at - i.created_at).total_seconds()/3600
       for i in repo.get_issues(state="closed", since=since)
       if i.pull_request is None and i.closed_at]

if dur:
    print(f"MTTR (últimos {WINDOW} días): {statistics.mean(dur):,.1f} h")
else:
    print("No se encontraron issues cerradas en el período.")
