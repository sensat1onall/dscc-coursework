import json
import ssl
import urllib.request

ctx = ssl.create_default_context()

# Check GitHub Actions
try:
    req = urllib.request.Request(
        "https://api.github.com/repos/sensat1onall/dscc-coursework/actions/runs?per_page=3",
        headers={"Accept": "application/vnd.github.v3+json", "User-Agent": "Python"},
    )
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        data = json.loads(resp.read())
        for run in data.get("workflow_runs", []):
            print(
                f"Run #{run['run_number']}: {run['status']} / {run.get('conclusion', 'N/A')}"
                f" - {run['display_title'][:70]}"
            )
except Exception as e:
    print(f"GitHub API error: {e}")

# Check live site
print("\n--- Checking live site ---")
try:
    req2 = urllib.request.Request("http://51.120.120.23/", headers={"User-Agent": "Python"})
    with urllib.request.urlopen(req2, timeout=10) as resp2:
        body = resp2.read().decode("utf-8", errors="replace")
        print(f"IP site status: {resp2.status}")
        if "TaskFlow" in body:
            print("NEW DESIGN DETECTED (TaskFlow branding found)")
        elif "Task Manager" in body:
            print("OLD DESIGN still showing")
        else:
            print("Unknown design")
        # Print a snippet
        idx = body.find("<title>")
        if idx >= 0:
            print(f"Title: {body[idx:idx+60]}")
except Exception as e:
    print(f"IP check error: {e}")
