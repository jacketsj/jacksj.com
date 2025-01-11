import os
import subprocess
import shutil
import sys
import tempfile

def run_command(command, cwd=None):
    """Run a shell command and handle errors."""
    result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {command}")
        print(result.stderr)
        sys.exit(1)
    return result.stdout.strip()

def generate_site(temp_dir):
    # Step 0: Update the submodule containing the site data
    print("Updating submodules...")
    run_command("git submodule update")
    # Step 1: Run generator.py inside pubdata
    print("Running generator.py to generate index.html...")
    run_command("python3 generator.py", cwd="pubdata")
    
    # Step 2: Copy generated index.html and .png files to the temporary directory
    print("Copying generated files to temporary directory...")
    shutil.copy("pubdata/index.html", temp_dir)
    shutil.copy("CNAME", temp_dir)

    for file in os.listdir("pubdata"):
        if file.endswith(".png"):
            shutil.copy(os.path.join("pubdata", file), temp_dir)

def switch_to_gh_pages():
    # Step 3: Checkout to gh-pages branch
    current_branch = run_command("git branch --show-current")
    print(f"Current branch: {current_branch}")

    global stash_needed
    stash_needed = False

    if current_branch != "gh-pages":
        print("Checking for uncommitted changes...")
        status = run_command("git status --porcelain")
        if status:
            print("Stashing uncommitted changes...")
            run_command("git stash")
            stash_needed = True

        print("Checking out gh-pages branch...")
        run_command("git checkout gh-pages")

def update_gh_pages(temp_dir):
    # Ensure we're on the gh-pages branch before deleting anything
    current_branch = run_command("git branch --show-current")
    if current_branch != "gh-pages":
        print("ERROR: Not on gh-pages branch! Aborting cleanup to prevent data loss.")
        sys.exit(1)

    # Step 4: Remove old site files but protect .git and .gitignore
    print("Cleaning up old files in gh-pages (except .git and .gitignore)...")
    for item in os.listdir():
        if item not in [".git", ".gitignore"]:
            if os.path.isdir(item):
                shutil.rmtree(item)
            else:
                os.remove(item)

    # Step 5: Copy new content from the temp directory
    print("Copying new site files to gh-pages...")
    for file in os.listdir(temp_dir):
        shutil.copy(os.path.join(temp_dir, file), ".")

    # Step 6: Commit and push changes
    print("Adding changes to git...")
    run_command("git add .")

    print("Committing changes...")
    try:
        run_command('git commit -m "Deploy updated site"')
    except SystemExit:
        print("No changes to commit.")

    print("Pushing to gh-pages...")
    run_command("git push origin gh-pages")

def return_to_main():
    print("Returning to main branch...")
    run_command("git checkout main")

    if stash_needed:
        print("Applying stashed changes...")
        run_command("git stash pop")

def main():
    # Use a safe temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        generate_site(temp_dir)
        switch_to_gh_pages()
        update_gh_pages(temp_dir)
        return_to_main()
    
    print("Deployment complete!")

if __name__ == "__main__":
    main()

