# How to update readme and index.html files

The files `README.md` and `index.html` are created from the notebook `moarchiving.ipynb`.
To update the files, make changes in the notebook, and then run the following commands:

```bash
jupyter nbconvert --to html --output index  moarchiving.ipynb 
 jupyter nbconvert --to markdown --output README  moarchiving.ipynb
python -c "s = open('README.md', 'r').read().split('### 11')[0]; open('README.md', 'w').write(s)"
```
