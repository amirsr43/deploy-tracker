import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "deploytrack.db"

def get_connection():
    DATA_DIR.mkdir(exist_ok=True)
    
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection

def initialize_database():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            repository TEXT,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deployments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            version TEXT NOT NULL,
            environment TEXT NOT NULL,
            branch TEXT,
            commit_hash TEXT,
            status TEXT NOT NULL,
            deployed_by TEXT,
            duration INTEGER DEFAULT 0,
            notes TEXT,
            error_reason TEXT,
            deployed_at DATETIME DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (project_id)
                REFERENCES projects(id)
                ON DELETE CASCADE
        )
    """)

    deployment_columns = {
        row["name"]
        for row in cursor.execute("PRAGMA table_info(deployments)")
    }
    if "error_reason" not in deployment_columns:
        cursor.execute(
            "ALTER TABLE deployments ADD COLUMN error_reason TEXT"
        )

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def backup_database(file_path):
    backup_path = Path(file_path).expanduser().resolve()
    database_path = DATABASE_PATH.resolve()
    if backup_path == database_path:
        raise ValueError("The backup path cannot overwrite the active database.")

    backup_path.parent.mkdir(parents=True, exist_ok=True)
    source = get_connection()
    destination = sqlite3.connect(backup_path)
    try:
        source.backup(destination)
    finally:
        destination.close()
        source.close()


def restore_database(file_path):
    backup_path = Path(file_path).expanduser().resolve()
    if not backup_path.is_file():
        raise FileNotFoundError("The backup file was not found.")
    if backup_path == DATABASE_PATH.resolve():
        raise ValueError("Choose a backup file, not the active database.")

    backup_uri = f"file:{backup_path.as_posix()}?mode=ro"
    source = sqlite3.connect(backup_uri, uri=True)
    try:
        integrity = source.execute("PRAGMA integrity_check").fetchone()
        if not integrity or integrity[0] != "ok":
            raise ValueError("The backup database is invalid or corrupted.")

        tables = {
            row[0]
            for row in source.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        if not {"projects", "deployments"}.issubset(tables):
            raise ValueError("This file is not a recognized DeployTrack backup.")

        project_columns = {
            row[1] for row in source.execute("PRAGMA table_info(projects)")
        }
        deployment_columns = {
            row[1] for row in source.execute("PRAGMA table_info(deployments)")
        }
        if not {"id", "name"}.issubset(project_columns) or not {
            "id", "project_id", "version", "environment", "status"
        }.issubset(deployment_columns):
            raise ValueError("The backup database has an incompatible schema.")

        destination = get_connection()
        try:
            source.backup(destination)
        finally:
            destination.close()
    finally:
        source.close()

    initialize_database()