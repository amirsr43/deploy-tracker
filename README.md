# DeployTrack

DeployTrack is a lightweight desktop application for recording and reviewing project deployments. It uses Python, CustomTkinter, and a local SQLite database.

## Features

- Track projects and deployment history.
- Record deployment environment, version, branch, commit, status, duration, notes, and failure reason.
- Search deployments and filter by status, project, or environment.
- Review recent activity and a small set of dashboard metrics.
- Export filtered deployment history to CSV or Excel.
- Choose a light, dark, or system theme.
- Back up and restore the local database.

> DeployTrack records deployment information; it does not run deployments or connect to a CI/CD provider.

## Screenshots

### Dashboard

![DeployTrack dashboard](https://github.com/user-attachments/assets/c8c8fe92-d6fb-4299-86df-24c90fdddeba)

### Deployments and filters

![Deployment history with filters](https://github.com/user-attachments/assets/003d6999-d5b0-4bc7-9a44-2364ed5d5ec6)

### Projects

![DeployTrack projects](https://github.com/user-attachments/assets/781aac92-654f-4549-9a2e-c4247e99e75e)

### New deployment

![New deployment form](https://github.com/user-attachments/assets/af74c515-07c3-4362-8280-14862883b424)

### Settings

![DeployTrack settings](https://github.com/user-attachments/assets/2b0fa430-f010-4cba-9459-c5209c77101e)

## Requirements

- Python 3.10 or newer
- pip

## Installation

Clone the repository, then create and activate a virtual environment.

### Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

### macOS and Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

The SQLite database is created automatically in `data/deploytrack.db` the first time the application runs. Local database files are excluded from Git.

## Tests

Run the standard-library test suite with:

```bash
python -m unittest discover -s tests -v
```

## Data and backups

Use **Settings → Create backup** to save a copy of the database. **Restore backup** replaces the current local data with the selected DeployTrack backup.
"# deploy-tracker" 
