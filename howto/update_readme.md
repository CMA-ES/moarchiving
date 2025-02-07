Files `README.md` and `index.html` are created from the notebook `moarchiving.ipynb`
To update the files, make changes in the notebook, and then run the following commands:

```bash
jupyter nbconvert --to markdown --output README  moarchiving.ipynb 
jupyter nbconvert --to html --output index  moarchiving.ipynb 
```