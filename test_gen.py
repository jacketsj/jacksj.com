#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys

def run(cmd, cwd=None):
    """Run a shell command; exit on failure."""
    print(f"> {cmd}  (cwd={cwd or os.getcwd()})")
    p = subprocess.run(cmd, shell=True, cwd=cwd,
                       capture_output=True, text=True)
    if p.returncode != 0:
        print(p.stderr, file=sys.stderr)
        sys.exit(p.returncode)
    return p.stdout.strip()

def build_test_site(out_dir):
    """Run generator.py in pubdata and copy artifacts to out_dir."""
    print("→ Generating site…")
    run("python3 generator.py", cwd="pubdata")

    if os.path.exists(out_dir):
        print(f"→ Cleaning existing {out_dir}…")
        shutil.rmtree(out_dir)
    
    os.makedirs(out_dir, exist_ok=True)

    # copy generated index.html
    shutil.copy(os.path.join("pubdata", "index.html"), out_dir)
    
    # copy CNAME from repo root
    if os.path.exists("CNAME"):
        shutil.copy("CNAME", out_dir)

    # copy all .png from pubdata
    for fname in os.listdir("pubdata"):
        if fname.lower().endswith(".png"):
            shutil.copy(os.path.join("pubdata", fname), out_dir)

    # copy all of docstore into out_dir/docstore, excluding the nocopy folder
    doc_src = "docstore"
    doc_dst = os.path.join(out_dir, "docstore")
    if os.path.isdir(doc_src):
        print("→ Copying docstore…")
        shutil.copytree(
            doc_src,
            doc_dst,
            ignore=shutil.ignore_patterns("nocopy")
        )

def main():
    # ensure we're in the repo root
    base = os.path.dirname(os.path.realpath(__file__))
    os.chdir(base)

    out_dir = "test_deploy"
    build_test_site(out_dir)
    print(f"✅ Test build complete! Files are in {out_dir}/")

if __name__ == "__main__":
    main()
