## Visualising your DNS records using neo4j

## Get started

```sh
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
git clone https://github.com/kubernetes/k8s.io.git 
python main.py
```

If you got this far, the script would have generated a file `domains.csv`. See `import.cql` for the schema.

### I've got my own octodns config

Change `ZONE_PATH` to the directory that contains your configs and repeat the above

### I want to explore the example data

1. Download `domains.csv`
2. Find your neo4j database and copy `domains.csv` to the `import` folder of the database.
3. Run `import.cql` or its contents directly in the neo4j browser.
