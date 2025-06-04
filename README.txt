# Instructions for setup/edits
1. Clone this repo.
2. Run `git submodule update --init' to get the `pubdata` repo as a submodule.
3. Add publications/make edits in pubdata repo (`pubs.yaml` and `generator.py`). Then commit/push to that repo.
4. Commit/push the submodule reference in this repo.
5. Create a python venv if necessary with `python3 -m venv venv`, `source venv/bin/activate`, `pip install -r requirements.txt`.
6. Run `python3 gen.py` to build and deploy.
7. Commit/push the changes to `index.html` (just to keep it up-to-date in main).
