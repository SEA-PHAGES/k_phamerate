"""Integration tests for the get_db pipeline."""

from pathlib import Path
import sys
import shutil
import unittest
from unittest.mock import patch

import sqlalchemy

from pdm_utils import run
from pdm_utils.classes.alchemyhandler import AlchemyHandler
from pdm_utils.pipelines import get_db

# Import helper functions to build mock database
unittest_file = Path(__file__)
test_dir = unittest_file.parent.parent
if str(test_dir) not in set(sys.path):
    sys.path.append(str(test_dir))
import test_db_utils

pipeline = "get_db"
DB = test_db_utils.DB
USER = test_db_utils.USER
PWD = test_db_utils.PWD
DB2 = "Actinobacteriophage"

# Create the main test directory in which all files will be
# created and managed. Gets created once for all tests.
test_root_dir = Path("/tmp", "pdm_utils_tests_get_db")
if test_root_dir.exists() == True:
    shutil.rmtree(test_root_dir)
test_root_dir.mkdir()

# Since these tests involve creating new databases, be sure to
# remove the existing test database if it is already present.
exists = test_db_utils.check_if_exists()
if exists:
    test_db_utils.remove_db()

# Within main test folder, this new folder will be created/removed
# for each test. Within the output_folder, get_db will dynamically create
# a new folder, but only if files are downloaded.
output_path = Path(test_root_dir, "output")
results_path = Path(output_path, get_db.RESULTS_FOLDER)

def get_unparsed_args(db=DB, option=None, download=False, output_folder=None):
    """Returns list of command line arguments to convert database."""
    unparsed_args = ["run.py", pipeline, db, option]
    if option == "file":
        unparsed_args.extend([str(test_db_utils.TEST_DB_FILEPATH)])
    elif option == "server":
        if download:
            unparsed_args.extend(["-d"])
        if output_folder is not None:
            unparsed_args.extend(["-o", str(output_folder)])
    else:
        pass
    return unparsed_args




class TestGetDb(unittest.TestCase):

    def setUp(self):
        output_path.mkdir()
        # Since these tests involve installing databases instead of
        # accessing them, do not specify a database, but instead leave as "".
        self.alchemist = AlchemyHandler(username=USER, password=PWD)
        self.alchemist.build_engine()

    def tearDown(self):
        shutil.rmtree(output_path)
        exists = test_db_utils.check_if_exists()
        if exists:
            test_db_utils.remove_db()


    @patch("pdm_utils.pipelines.get_db.establish_database_connection")
    def test_main_1(self, edc_mock):
        """Verify database is installed from file."""
        edc_mock.return_value = self.alchemist
        unparsed_args = get_unparsed_args(option="file")
        run.main(unparsed_args)
        # Query for version data. This verifies that the databases exists
        # and that it contains a pdm_utils schema with data.
        version_data = test_db_utils.get_data(test_db_utils.version_table_query)
        self.assertEqual(len(version_data), 1)


    @patch("pdm_utils.pipelines.get_db.establish_database_connection")
    def test_main_2(self, edc_mock):
        """Verify new database is created."""
        edc_mock.return_value = self.alchemist
        unparsed_args = get_unparsed_args(option="new")
        run.main(unparsed_args)

        # Query for version data. This verifies that the databases exists
        # and that it contains a pdm_utils schema with data.
        version_data = test_db_utils.get_data(test_db_utils.version_table_query)
        self.assertEqual(len(version_data), 1)


    @patch("pdm_utils.pipelines.get_db.establish_database_connection")
    def test_main_3(self, edc_mock):
        """Verify database is downloaded and installed from server."""
        edc_mock.return_value = self.alchemist
        # Since the entire Actinobacteriophage database is being downloaded,
        # be sure to only download the SQL file and do NOT install it,
        # else it will overwrite the existing Actinobacteriophage database.
        # Since the pdm_anon user is calling this pipeline, and since
        # this user should not have MySQL privileges to do anything other
        # than select data from Actinobacteriophage, this shouldn't be a problem.
        unparsed_args = get_unparsed_args(db=DB2, option="server",
                                          download=True, output_folder=output_path)
        run.main(unparsed_args)
        file1 = Path(results_path, f"{DB2}.sql")
        file2 = Path(results_path, f"{DB2}.version")
        with self.subTest():
            self.assertTrue(file1.exists())
        with self.subTest():
            self.assertTrue(file2.exists())


    @patch("pdm_utils.pipelines.get_db.establish_database_connection")
    def test_main_4(self, edc_mock):
        """Verify database is installed from file and overwrites
        existing database."""
        edc_mock.return_value = self.alchemist
        # First install a database with data. Then delete version table.
        test_db_utils.create_filled_test_db()
        test_db_utils.execute("DROP TABLE version")
        unparsed_args = get_unparsed_args(option="file")
        run.main(unparsed_args)
        # Now query for version data. This verifies that it replaced
        # the first database.
        version_data = test_db_utils.get_data(test_db_utils.version_table_query)
        self.assertEqual(len(version_data), 1)


if __name__ == '__main__':
    unittest.main()
