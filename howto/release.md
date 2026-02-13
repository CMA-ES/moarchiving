Starting:

merge development branch to master if necessary

Testing:

```sh
    python -m moarchiving.test
    ruff check --ignore F401 --ignore E722 --ignore E741 moarchiving
```

Final final changes to version numbers etc.:

```sh
    __init__.py  # edit version number
    moarchiving.ipynb  # add release description
    README.md + .html  # created from moarchiving.ipynb
        # from howto/update_readme.md:
        jupyter nbconvert --to html --output index  moarchiving.ipynb
        jupyter nbconvert --to markdown --output README  moarchiving.ipynb
        python -c "s = open('README.md', 'r').read().split('### 11')[0]; open('README.md', 'w').write(s)"
```

Create a distribution, assuming the folder `moarchiving` is linked as `src/moarchiving`.

```sh
    python -m build > dist_call_output.txt
    less dist_call_output.txt  # not very informative
    ll dist  # just checking creation date
    tar -tf dist/moarchiving-1.1.0.tar.gz | tree --fromfile | less  # check that the distribution folders are clean
```

Check distribution

```sh
    twine check dist/*1.1.*  # install/update/upgrade pkginfo if this fails
```

Finally, upload the distribution:

```sh
    twine upload dist/*1.1.x*  # to not upload outdated stuff
```

### Previous Way
To prepare a distribution from a dirty code folder:

```sh
    # CAVEAT: backup is also a homebrew minitool (not meant here)
    backup install-folder --move
    backup moarchiving --move 
    mkdir install-folder
    git checkout -- moarchiving
    cp -r moarchiving pyproject.toml LICENSE install-folder
    backup --recover  # recover last above moved folder (and backup current, just in case)
```

Make distribution

```sh
    cd install-folder
    python -c "s = open('../README.md', 'r').read().split('### 11')[0]; open('README.md', 'w').write(s)"
    python -m build > dist_call_output.txt
    less dist_call_output.txt  # not very informative
    ll dist  # just checking creation date
    tar -tf dist/moarchiving-1.0.0.tar.gz | tree --fromfile | less  # check that the distribution folders are clean
```

Check distribution and project description:

```sh
    twine check dist/*  # install/update/upgrade pkginfo if this fails
    cp dist/* ../dist
```

Copy changes in install-folder to root folder and commit (not clear how exactly, Diff Folders may help).

Finally, upload the distribution:

```sh
    twine upload dist/*1.0.x*  # to not upload outdated stuff
```

With `setuptools_scm`:

      -> expected: ERROR setuptools_scm._file_finders.git listing git files failed - pretending there aren't any
