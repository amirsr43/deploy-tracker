import csv
import tempfile
import unittest
from pathlib import Path

import database
import models


class DeploymentModelTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.previous_data_dir = database.DATA_DIR
        self.previous_database_path = database.DATABASE_PATH
        database.DATA_DIR = Path(self.temp_dir.name) / "data"
        database.DATABASE_PATH = database.DATA_DIR / "deploytrack.db"
        database.initialize_database()

    def tearDown(self):
        database.DATA_DIR = self.previous_data_dir
        database.DATABASE_PATH = self.previous_database_path
        self.temp_dir.cleanup()

    def test_search_filters_by_status_project_and_environment(self):
        first_project = models.create_project("API")
        second_project = models.create_project("Dashboard")
        models.create_deployment(
            first_project,
            "v1.0.0",
            "Production",
            status="Failed"
        )
        models.create_deployment(
            first_project,
            "v1.0.1",
            "Staging",
            status="Success"
        )
        models.create_deployment(
            second_project,
            "v2.0.0",
            "Production",
            status="Failed"
        )

        results = models.search_deployments(
            environment="Production",
            status="Failed",
            project_id=first_project
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["project_name"], "API")
        self.assertEqual(results[0]["version"], "v1.0.0")

    def test_csv_export_uses_active_filters(self):
        project_id = models.create_project("API")
        models.create_deployment(
            project_id,
            "v1.0.0",
            "Production",
            status="Failed",
            error_reason="Health check timed out"
        )
        models.create_deployment(
            project_id,
            "v1.0.1",
            "Staging",
            status="Success"
        )
        export_path = Path(self.temp_dir.name) / "filtered.csv"

        models.export_deployments_to_csv(
            export_path,
            status="Failed",
            project_id=project_id
        )

        with export_path.open(encoding="utf-8-sig", newline="") as export_file:
            rows = list(csv.DictReader(export_file))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["Version"], "v1.0.0")
        self.assertEqual(rows[0]["Failure Reason"], "Health check timed out")

    def test_backup_restore_recovers_database_contents(self):
        models.create_project("Original")
        backup_path = Path(self.temp_dir.name) / "backup.db"
        database.backup_database(backup_path)
        models.create_project("Temporary")

        database.restore_database(backup_path)

        self.assertEqual(models.count_projects(), 1)
        self.assertEqual(models.get_projects()[0]["name"], "Original")


if __name__ == "__main__":
    unittest.main()
