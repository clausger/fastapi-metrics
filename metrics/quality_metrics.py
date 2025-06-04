import pathlib, csv, statistics, subprocess, json, os, datetime
from radon.complexity import cc_visit, SCORE
from github import Github

REPO_URL  = "https://github.com/tiangolo/fastapi.git"
LOCAL_DIR = pathlib.Path("fastapi")
TOKEN     = os.getenv("GITHUB_TOKEN")
MONTHS    = 12
CSV_OUT   = pathlib.Path("complexity.csv")

# Clona o actualiza FastAPI
if not LOCAL_DIR.exists():
    subprocess.run(["git", "clone", "--depth", "1", REPO_URL, LOCAL_DIR.name], check=True)
else:
    subprocess.run(["git", "-C", LOCAL_DIR, "pull", "--ff-only"], check=True)

# Complejidad ciclomática
records = []
for f in LOCAL_DIR.rglob("*.py"):
    try:
        blocks = cc_visit(f.read_text("utf-8", "ignore"))
    except SyntaxError:
        continue
    for b in blocks:
        records.append({"file": str(f.relative_to(LOCAL_DIR)),
                        "name": b.name,
                        "complexity": b.complexity,
                        "rank": SCORE.grading(b.complexity)})

with CSV_OUT.open("w", newline="") as fp:
    writer = csv.DictWriter(fp, fieldnames=records[0])
    writer.writeheader()
    writer.writerows(records)

avg = statistics.fmean(r["complexity"] for r in records)
print(f"Complejidad promedio: {avg:.2f}")

# Densidad de defectos (issues / KLOC)
cloc_out = subprocess.check_output(["cloc", "--json", LOCAL_DIR], text=True)
loc = json.loads(cloc_out)["Python"]["code"] / 1000  # KLOC

since = datetime.datetime.utcnow() - datetime.timedelta(days=30*MONTHS)
gh = Github(TOKEN); repo = gh.get_repo("tiangolo/fastapi")
defects = sum(1 for i in repo.get_issues(state="closed", since=since) if not i.pull_request)
print(f"Densidad de defectos (últimos {MONTHS} meses): {defects/loc:.2f} issues/KLOC")
