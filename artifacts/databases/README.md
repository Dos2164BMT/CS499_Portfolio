# Network Automation: Database Enhancement

The `original` folder is the Algorithms enhancement before persistence. The `enhanced`
folder adds normalized SQLite storage, parameterized queries, transaction handling,
audit events, bounded execution history, and six database-focused tests.

```bash
cd enhanced
python3 -m unittest discover -s tests -v
python3 run.py --inventory data/inventory.json --requests data/requests.json --database automation.db
python3 run.py --database automation.db --history 10
```

Credentials and private keys are deliberately excluded from the database.
