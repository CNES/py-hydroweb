# Py Hydroweb

## Publish a new package version on PyPi

First of all, update version in pyproject.toml and setup.cfg and then:

```console
rm -rf dist/*
python3 -m pip install --upgrade build
python3 -m build
python3 -m pip install --upgrade twine
python3 -m twine upload dist/*
```

Please note that last command will ask for a valid PyPi API token with maintainer rights on the https://pypi.org/project/py-hydroweb/ project.

Finally we need to update the `latest_version` param in the front templated python script in order to inform our users that a newer version is available.