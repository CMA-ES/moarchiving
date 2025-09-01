To update the apidocs, run the following command in the terminal (you might need to run it as an administrator):
```bash
git switch gh-pages
git merge development  # try rebase when merge fails, afterwards git pull --rebase
pydoctor --html-output=moarchiving-apidocs --docformat=restructuredtext moarchiving  # RST finds more links
git add moarchiving-apidocs  # also adds new files
git commit -a
git push
```
