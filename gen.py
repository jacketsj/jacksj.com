#!/usr/bin/env python3
import os
import subprocess
import shutil
import sys
import tempfile

def run(cmd, cwd=None):
    """Run a shell command; exit on failure."""
    print(f"> {cmd}  (cwd={cwd or os.getcwd()})")
    p = subprocess.run(cmd, shell=True, cwd=cwd,
                       capture_output=True, text=True)
    if p.returncode != 0:
        print(p.stderr, file=sys.stderr)
        sys.exit(p.returncode)
    return p.stdout.strip()

def update_pubdata():
    """Init submodule, switch to master, pull latest."""
    print("→ Updating pubdata submodule…")
    run("git submodule update --init --recursive")
    run("git fetch origin master", cwd="pubdata")
    run("git checkout master",   cwd="pubdata")
    run("git pull",              cwd="pubdata")

def build_site(out_dir):
    """Run generator.py in pubdata and copy artifacts + root CNAME to out_dir."""
    update_pubdata()
    print("→ Generating site…")
    run("python3 generator.py", cwd="pubdata")

    os.makedirs(out_dir, exist_ok=True)
    # copy generated index.html
    shutil.copy(os.path.join("pubdata", "index.html"), out_dir)
    # copy CNAME from repo root (not pubdata)
    shutil.copy("CNAME", out_dir)

    # copy all .png from pubdata
    for fname in os.listdir("pubdata"):
        if fname.lower().endswith(".png"):
            shutil.copy(os.path.join("pubdata", fname), out_dir)

    # copy all of docstore into out_dir/docstore, excluding the nocopy folder
    doc_src = "docstore"
    doc_dst = os.path.join(out_dir, "docstore")
    if os.path.isdir(doc_src):
        shutil.copytree(
            doc_src,
            doc_dst,
            ignore=shutil.ignore_patterns("nocopy")
        )

def deploy_site(build_dir):
    """
    Clone gh-pages into a fresh temp folder, reset it to origin,
    wipe everything but .git/.gitignore, then copy in build_dir and push.
    """
    print("→ Cloning gh-pages branch into temp…")
    remote = run("git config --get remote.origin.url")
    gh_dir = os.path.join(build_dir, "gh-pages")
    run(f"git clone --branch gh-pages --single-branch {remote} {gh_dir}")

    print("→ Resetting to origin/gh-pages to avoid conflicts…")
    run("git fetch origin gh-pages", cwd=gh_dir)
    run("git reset --hard origin/gh-pages", cwd=gh_dir)

    print("→ Cleaning old files…")
    for item in os.listdir(gh_dir):
        if item in (".git", ".gitignore"):
            continue
        path = os.path.join(gh_dir, item)
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

    print("→ Copying new site into gh-pages…")
    for item in os.listdir(build_dir):
        if item == "gh-pages":
            continue
        src = os.path.join(build_dir, item)
        dst = os.path.join(gh_dir, item)
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)

    print("→ Committing and pushing gh-pages…")
    run("git add .", cwd=gh_dir)
    try:
        run('git commit -m "Deploy updated site"', cwd=gh_dir)
    except SystemExit:
        print("   (nothing to commit)")
    run("git push origin gh-pages", cwd=gh_dir)

def main():
    # ensure we're in the repo root
    base = os.path.dirname(os.path.realpath(__file__))
    os.chdir(base)

    with tempfile.TemporaryDirectory() as tmp:
        build_dir = os.path.join(tmp, "build")
        build_site(build_dir)
        deploy_site(build_dir)
    print("✅ Deployment complete!")

if __name__ == "__main__":
    main()

