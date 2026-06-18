#lib/gitops.py
import subprocess                           #lets python shell out to the git binary
from datetime import datetime               #for the default timestamped commit message

def git_commit(paths, message=None):
    #if no message passed, default to a timestamp so a bare call is still traceable
    if message is None:
        message = f"Auto-commit {datetime.now():%Y-%m-%d %H:%M:%S}"

    #Stage the paths. check=True means a FAILED 'git add' raises - that IS an error
    #*paths unpacks the list: ["git","add", "backups/", "scripts/18_..."]
    subprocess.run(["git", "add", *paths], check=True)

    #Commit. NOTE: no check=True here on purpose.
    #git returns a NON-ZERO code when there is nothing to commit, and
    #"nothing changed" is a valid idempotent outcome - not a crash.
    result = subprocess.run(["git", "commit", "-m", message])

    #so we branch on the return code instead of letting it throw.
    if result.returncode == 0:
        print(f"[gitops] committed: {message}")
    else:
        print("[gitops] nothing to commit - working tree clean")
        
