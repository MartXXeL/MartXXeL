
from __future__ import annotations

import datetime as dt
import html
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

UA = "Mozilla/5.0 (compatible; profile-generator/1.0; +https://github.com/MartXXeL)"

WINDOW_DAYS = 364

def utc_window(today: dt.date | None = None) -> tuple[str, str, dt.date, dt.date]:
    today = today or dt.datetime.now(dt.timezone.utc).date()
    start = today - dt.timedelta(days=WINDOW_DAYS)
    return (
        f"{start.isoformat()}T00:00:00Z",
        f"{today.isoformat()}T23:59:59Z",
        start,
        today,
    )

def _get(url: str, token: str | None = None, accept: str = "application/json") -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()

QUERY = """
query($login:String!,$from:DateTime!,$to:DateTime!){
  user(login:$login){
    login name avatarUrl createdAt bio location
    followers{totalCount}
    contributionsCollection(from:$from,to:$to){
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalPullRequestReviewContributions
      totalRepositoriesWithContributedCommits
      contributionCalendar{
        totalContributions
        weeks{ contributionDays{ date contributionCount weekday } }
      }
    }
    repositories(first:100, ownerAffiliations:OWNER, privacy:PUBLIC, isFork:false,
                 orderBy:{field:PUSHED_AT,direction:DESC}){
      totalCount
      nodes{
        name description url stargazerCount forkCount pushedAt isArchived
        primaryLanguage{ name color }
      }
    }
  }
}
"""

def via_graphql(login: str, token: str) -> dict:
    frm, to, _, _ = utc_window()
    payload = json.dumps(
        {"query": QUERY, "variables": {"login": login, "from": frm, "to": to}}
    ).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "User-Agent": UA,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        body = json.load(r)
    if "errors" in body:
        raise RuntimeError(body["errors"])

    u = body["data"]["user"]
    cc = u["contributionsCollection"]
    cal = cc["contributionCalendar"]

    days = [
        {"date": d["date"], "count": d["contributionCount"]}
        for w in cal["weeks"]
        for d in w["contributionDays"]
    ]

    repos = []
    for n in u["repositories"]["nodes"]:
        repos.append(
            {
                "name": n["name"],
                "description": n["description"] or "",
                "url": n["url"],
                "stars": n["stargazerCount"],
                "forks": n["forkCount"],
                "pushed_at": n["pushedAt"][:10],
                "language": (n["primaryLanguage"] or {}).get("name"),
                "archived": n["isArchived"],
            }
        )

    return _assemble(
        login=u["login"],
        name=u["name"] or u["login"],
        created_at=u["createdAt"][:10],
        followers=u["followers"]["totalCount"],
        days=days,
        repos=repos,
        repo_total=u["repositories"]["totalCount"],
        breakdown={
            "commits": cc["totalCommitContributions"],
            "pull_requests": cc["totalPullRequestContributions"],
            "issues": cc["totalIssueContributions"],
            "reviews": cc["totalPullRequestReviewContributions"],
            "repos_touched": cc["totalRepositoriesWithContributedCommits"],
        },
        source="graphql",
    )

DAY_RE = re.compile(
    r'<td[^>]*?data-date="(?P<date>\d{4}-\d{2}-\d{2})"[^>]*?id="(?P<id>[^"]+)"[^>]*?'
    r'data-level="(?P<level>\d)"',
    re.S,
)
TIP_RE = re.compile(r'<tool-tip[^>]*?for="(?P<id>[^"]+)"[^>]*?>(?P<text>.*?)</tool-tip>', re.S)
COUNT_RE = re.compile(r"^\s*(\d+)\s+contribution")

LINGUIST = {
    "Python": "#3572A5", "Java": "#b07219", "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6", "HTML": "#e34c26", "CSS": "#563d7c",
    "C": "#555555", "C++": "#f34b7d", "C#": "#178600", "Go": "#00ADD8",
    "Rust": "#dea584", "Shell": "#89e051", "Ruby": "#701516", "PHP": "#4F5D95",
    "Kotlin": "#A97BFF", "Swift": "#F05138", "Dart": "#00B4AB", "R": "#198CE7",
    "Jupyter Notebook": "#DA5B0B", "SQL": "#e38c00", "Makefile": "#427819",
    "Dockerfile": "#384d54", "Vue": "#41b883", "Svelte": "#ff3e00",
    "Assembly": "#6E4C13", "Lua": "#000080", "Perl": "#0298c3",
    "PowerShell": "#012456", "Batchfile": "#C1F12E", "Haskell": "#5e5086",
    "Scala": "#c22d40", "Elixir": "#6e4a7e", "Clojure": "#db5855",
    "TeX": "#3D6117", "Markdown": "#083fa1", "Roff": "#ecdebe",
}

def via_public(login: str) -> dict:
    raw = _get(
        f"https://github.com/users/{login}/contributions",
        accept="text/html",
    ).decode("utf-8", "replace")

    tips = {m["id"]: html.unescape(m["text"]).strip() for m in TIP_RE.finditer(raw)}
    days = []
    for m in DAY_RE.finditer(raw):
        tip = tips.get(m["id"], "")
        hit = COUNT_RE.match(tip)
        count = int(hit.group(1)) if hit else 0
        if count == 0 and m["level"] != "0":
            count = int(m["level"])
        days.append({"date": m["date"], "count": count})
    days.sort(key=lambda d: d["date"])
    if not days:
        raise RuntimeError("could not parse the public contributions calendar")

    user = json.loads(_get(f"https://api.github.com/users/{login}"))
    raw_repos = json.loads(
        _get(f"https://api.github.com/users/{login}/repos?per_page=100&type=owner&sort=pushed")
    )

    repos = []
    for r in raw_repos:
        if r["fork"]:
            continue
        repos.append(
            {
                "name": r["name"],
                "description": r["description"] or "",
                "url": r["html_url"],
                "stars": r["stargazers_count"],
                "forks": r["forks_count"],
                "pushed_at": r["pushed_at"][:10],
                "language": r["language"],
                "archived": r["archived"],
            }
        )

    return _assemble(
        login=user["login"],
        name=user["name"] or user["login"],
        created_at=user["created_at"][:10],
        followers=user["followers"],
        days=days,
        repos=repos,
        repo_total=len(repos),
        breakdown=None,
        source="public",
    )

def streaks(days: list[dict]) -> dict:
    runs, run = [], []
    for d in days:
        if d["count"] > 0:
            run.append(d)
        elif run:
            runs.append(run)
            run = []
    if run:
        runs.append(run)

    def shape(r: list[dict]) -> dict:
        return {
            "length": len(r),
            "start": r[0]["date"] if r else None,
            "end": r[-1]["date"] if r else None,
        }

    longest = max(runs, key=len) if runs else []

    today = days[-1]
    current: list[dict] = []
    tail = days[:-1] if today["count"] == 0 else days
    for d in reversed(tail):
        if d["count"] > 0:
            current.insert(0, d)
        else:
            break

    return {"current": shape(current), "longest": shape(longest)}

def _assemble(**kw) -> dict:
    days = kw["days"]
    total = sum(d["count"] for d in days)
    best = max(days, key=lambda d: d["count"])

    weeks: list[dict] = []
    for i in range(0, len(days), 7):
        chunk = days[i : i + 7]
        weeks.append(
            {"start": chunk[0]["date"], "total": sum(d["count"] for d in chunk)}
        )

    active = [d for d in days if d["count"] > 0]
    return {
        "login": kw["login"],
        "name": kw["name"],
        "created_at": kw["created_at"],
        "followers": kw["followers"],
        "source": kw["source"],
        "window": {"from": days[0]["date"], "to": days[-1]["date"], "days": len(days)},
        "days": days,
        "weeks": weeks,
        "totals": {
            "year": total,
            "active_days": len(active),
            "best_day": {"date": best["date"], "count": best["count"]},
            "repos": kw["repo_total"],
        },
        "breakdown": kw["breakdown"],
        "streak": streaks(days),
        "languages": [],
        "repos": kw["repos"],
    }

def survey_repos(content: dict, owned: list[dict]) -> tuple[list[dict], list[dict]]:
    import repo_stats

    identities = {e.lower() for e in content.get("identities", [])}
    listed = [e["repo"] for e in content.get("collaborations", [])]
    extra = [r["name"] for r in owned]

    seen: set[str] = set()
    order: list[str] = []
    for full in listed + [f"{content.get('login', '')}/{n}" for n in extra]:
        if "/" in full and full not in seen:
            seen.add(full)
            order.append(full)

    collabs, lang_bytes, lang_repos = [], {}, {}
    for full in order:
        s = repo_stats.survey(full, identities)
        if s is None:
            continue
        if s["repo"] in listed:
            collabs.append({k: v for k, v in s.items() if k != "languages"})
        if s["mine"] == 0:
            continue
        for name, size in s["languages"].items():
            lang_bytes[name] = lang_bytes.get(name, 0) + size
            lang_repos[name] = lang_repos.get(name, 0) + 1

    total = sum(lang_bytes.values()) or 1
    languages = [
        {
            "name": n,
            "bytes": b,
            "pct": round(100 * b / total, 1),
            "repos": lang_repos.get(n, 0),
            "color": LINGUIST.get(n, "#8b949e"),
        }
        for n, b in sorted(lang_bytes.items(), key=lambda kv: -kv[1])
    ]
    collabs.sort(key=lambda c: listed.index(c["repo"]))
    return collabs, languages

def collect(login: str, token: str | None) -> dict:
    if token:
        try:
            return via_graphql(login, token)
        except Exception as exc:
            print(f"  graphql failed ({exc}); falling back to the public path", file=sys.stderr)
    return via_public(login)

def main() -> int:
    login = os.environ.get("GH_LOGIN", "MartXXeL")
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    survey_only = "--survey-only" in sys.argv

    DATA.mkdir(exist_ok=True)
    out = DATA / "profile.json"

    if survey_only and out.exists():
        profile = json.loads(out.read_text(encoding="utf-8"))
    else:
        profile = collect(login, token)

    content = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))
    content["login"] = login

    collabs, languages = survey_repos(content, profile["repos"])
    profile["collaborations"] = collabs
    if languages:
        profile["languages"] = languages

    out.write_text(
        json.dumps(profile, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    t = profile["totals"]
    s = profile["streak"]
    print(
        f"  {profile['login']}  via {profile['source']}  "
        f"{t['year']} contributions / {t['active_days']} active days / "
        f"streak {s['current']['length']} (best {s['longest']['length']})"
    )
    return 0

if __name__ == "__main__":
    sys.exit(main())
