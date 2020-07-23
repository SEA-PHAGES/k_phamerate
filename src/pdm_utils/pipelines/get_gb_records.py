"""Pipeline to retrieve GenBank records using accessions stored in the MySQL database."""

import argparse
import configparser
import os
import re
import shutil
import sys
import time
from datetime import date
from pathlib import Path

from Bio import SeqIO

from pdm_utils.classes.filter import Filter
from pdm_utils.classes.alchemyhandler import AlchemyHandler
from pdm_utils.functions import basic
from pdm_utils.functions import configfile
from pdm_utils.functions import fileio
from pdm_utils.functions import ncbi
from pdm_utils.functions import mysqldb
from pdm_utils.functions import mysqldb_basic
from pdm_utils.functions import pipelines_basic
from pdm_utils.functions import parsing
from pdm_utils.functions import querying

#GLOBAL VARIABLES
#-----------------------------------------------------------------------------
DEFAULT_FOLDER_NAME = f"{time.strftime('%Y%m%d')}_gb_records"
DEFAULT_FOLDER_PATH = Path.cwd()
FILTER_KEY = "phage"

RECORD_FILE_TYPES = ["gb", "tbl"]
RETTYPE_MAPPINGS  = {"gb"  : "gb",
                     "tbl" : "ft"}

#MAIN FUNCTIONS
#-----------------------------------------------------------------------------
# TODO unittest.
def main(unparsed_args_list):
    """Run main get_gb_records pipeline."""
    # Parse command line arguments
    args = parse_args(unparsed_args_list)

    # Create config object with data obtained from file and/or defaults.
    config = configfile.build_complete_config(args.config_file) 
    
    alchemist = pipelines_basic.build_alchemist(args.database, config=config)
    mysqldb.check_schema_compatibility(alchemist.engine, 
                                       "the get_gb_records pipeline")
    
    values = pipelines_basic.parse_value_input(args.input)

    execute_get_gb_records(alchemist, args.folder_path, args.folder_name, 
                           args.file_type, config=None,
                           values=values, verbose=args.verbose, 
                           filters=args.filters, groups=args.groups)
     
# TODO unittest.
def parse_args(unparsed_args_list):
    """Parses export_db arguments and stores them with an argparse object.

    :param unparsed_args_list: Input a list of command line args.
    :type unparsed_args_list: list[str]
    :returns: ArgParse module parsed args.
    """
    DATABASE_HELP = "Name of the MySQL database to export from."

    CONFIG_FILE_HELP = """
        Get gb record to the config file path specifying MySQL and NCBI credentials.
        """
    VERBOSE_HELP = """
        Get gb record option that enables progress print statements.
        """
    FOLDER_PATH_HELP = """
        Get gb record option to change the path
        of the directory where the exported files are stored.
            Follow selection argument with the path to the
            desired export directory.
        """
    FOLDER_NAME_HELP = """
        Export option to change the name
        of the directory where the exported files are stored.
            Follow selection argument with the desired name.
        """

    FILE_TYPE_HELP = """
        Get gb record option to select the file type retrieved from GenBank
            Follow selection argument with the desired file type.
        """

    IMPORT_FILE_HELP = """
        Selection input option that imports values from a csv file.
            Follow selection argument with path to the
            csv file containing the names of each genome in the first column.
        """
    SINGLE_GENOMES_HELP = """
        Selection input option that imports values from cmd line input.
            Follow selection argument with space separated
            names of genomes in the database.
        """
    TABLE_HELP = """
        Selection option that changes the table in the database selected from.
            Follow selection argument with a valid table from the database.
        """
    WHERE_HELP = """
        Data filtering option that filters data by the inputted expressions.
            Follow selection argument with formatted filter expression:
                {Table}.{Column}={Value}
        """
    GROUP_BY_HELP = """
        Data selection option that groups data by the inputted columns.
            Follow selection argument with formatted column expressions:
                {Table}.{Column}={Value}
        """
    parser = argparse.ArgumentParser()
    parser.add_argument("database", type=str, help=DATABASE_HELP)

    parser.add_argument("-c", "--config_file", 
                                type=pipelines_basic.convert_file_path,
                                help=CONFIG_FILE_HELP)
    parser.add_argument("-m", "--folder_name",
                                type=str, help=FOLDER_NAME_HELP)
    parser.add_argument("-o", "--folder_path", 
                                type=pipelines_basic.convert_dir_path,
                                help=FOLDER_PATH_HELP)
    parser.add_argument("-v", "--verbose", action="store_true",
                                help=VERBOSE_HELP)

    parser.add_argument("-ft", "--file_type", choices=RECORD_FILE_TYPES,
                                type=str, 
                                help=FILE_TYPE_HELP)
 
    parser.add_argument("-if", "--import_file", dest="input",
                                type=pipelines_basic.convert_file_path,
                                help=IMPORT_FILE_HELP)
    parser.add_argument("-in", "--import_names", nargs="*", dest="input",
                                help=SINGLE_GENOMES_HELP)
    parser.add_argument("-f", "--where", nargs="?", dest="filters",
                                help=WHERE_HELP)
    parser.add_argument("-g", "--group_by", nargs="*", dest="groups",
                                help=GROUP_BY_HELP)

    parser.set_defaults(file_type="gb",
                        folder_name=DEFAULT_FOLDER_NAME,
                        folder_path=DEFAULT_FOLDER_PATH,
                        verbose=False, input=[],
                        filters="", groups=[], sort=[])

    parsed_args = parser.parse_args(unparsed_args_list[2:])    
    return parsed_args

def execute_get_gb_records(alchemist, folder_path, folder_name, file_type, 
                           config=None, values=None, verbose=False, 
                           filters="", groups=[]):
    """Executes the entirety of the get_gb_records pipeline

    :param alchemist: A connected and fully build AlchemyHandler object.
    :type alchemist: AlchemyHandler
    :param folder_path: Path to a valid dir for new dir creation.
    :type folder_path: Path
    :param folder_name: A name for the export folder.
    :type folder_name: str
    :param file_type: File type to be exported.
    :type file_type: str
    :param config: ConfigParser object containing NCBI credentials.
    :type config: ConfigParser
    :param values: List of values to filter database results.
    :type values: list[str]
    :param verbose: A boolean value to toggle progress print statemtns.
    :type verbose: bool
    :param filters: A List of lists with filter value,grouped by ORs.
    :type filter: str
    :param groups: A list of supported MySQL column names to goup by.
    :type groups: list[str]
    """
    ncbi_creds = {}
    if not config is None:
        ncbi_creds = config["ncbi"] 

    db_filter = pipelines_basic.build_filter(alchemist, FILTER_KEY, filters,
                                                        values=values,
                                                        verbose=verbose) 

    records_path = folder_path.joinpath(folder_name)
    records_path = basic.make_new_dir(folder_path, records_path, attempt=50)

    conditionals_map = {}
    pipelines_basic.build_groups_map(db_filter, records_path, conditionals_map,
                                     groups=groups, verbose=verbose)

    values = db_filter.values
    for mapped_path in conditionals_map.keys():
        db_filter.reset()
        db_filter.values = values

        conditionals = conditionals_map[mapped_path]
        db_filter.values = db_filter.build_values(where=conditionals)

        # Create data sets
        if verbose:
            print("Retrieving accessions from the database...")
        accession_data = db_filter.select(["phage.PhageID", "phage.Accession"])

        acc_id_dict = {}
        for data_dict in accession_data:
            accession = data_dict["Accession"]
            if not (accession is None or accession == ""):
                acc_id_dict[accession] = data_dict["PhageID"]

        if len(acc_id_dict.keys()) > 0:
            ncbi_handle = get_verified_data_handle(mapped_path, acc_id_dict, 
                                 ncbi_cred_dict=ncbi_creds, file_type=file_type)

            copy_gb_data(ncbi_handle, acc_id_dict, mapped_path, file_type, 
                                                            verbose=verbose)
        else:
            print("There are no records to retrieve.")
            shutil.rmtree(records_path)
            sys.exit(1)

# TODO move to ncbi.
# TODO test.
def get_verified_data_handle(records_path, acc_id_dict, ncbi_cred_dict={}, 
                                                batch_size=200, file_type="gb"):
    """Retrieve genomes from GenBank.

    output_folder = Path to where files will be saved.
    acc_id_dict = Dictionary where key = Accession and value = List[PhageIDs]
    """

    # More setup variables if NCBI updates are desired.  NCBI Bookshelf resource
    # "The E-utilities In-Depth: Parameters, Syntax and More", by Dr. Eric
    # Sayers, recommends that a single request not contain more than about 200
    # UIDS so we will use that as our batch size, and all Entrez requests must
    # include the user's email address and tool name.
    ncbi.set_entrez_credentials(
        tool=ncbi_cred_dict.get("tool"),
        email=ncbi_cred_dict.get("email"),
        api_key=ncbi_cred_dict.get("api_key"))


    # Use esearch to verify the accessions are valid and efetch to retrieve
    # the record
    # Create batches of accessions
    unique_accession_list = list(acc_id_dict.keys())

    # Add [ACCN] field to each accession number
    appended_accessions = \
        [accession + "[ACCN]" for accession in unique_accession_list]


    # When retrieving in batch sizes, first create the list of values
    # indicating which indices of the unique_accession_list should be used
    # to create each batch.
    # For instace, if there are five accessions, batch size of two produces
    # indices = 0,2,4

    chunked_accessions = basic.partition_list(appended_accessions, batch_size)
    for chunk in chunked_accessions:
        delimiter = " | "
        esearch_term = delimiter.join(chunk)

        # Use esearch for each accession
        search_record = ncbi.run_esearch(db="nucleotide", term=esearch_term,
                            usehistory="y")
        search_count = int(search_record["Count"])
        search_webenv = search_record["WebEnv"]
        search_query_key = search_record["QueryKey"]
        summary_records = ncbi.get_summaries(db="nucleotide",
                                             query_key=search_query_key,
                                             webenv=search_webenv)

        accessions_to_retrieve = ncbi.get_accessions_to_retrieve(
                                                                summary_records)
        if len(accessions_to_retrieve) > 0: 
            fetch_handle = ncbi.get_data_handle(accessions_to_retrieve,
                                            rettype=RETTYPE_MAPPINGS[file_type])
            return fetch_handle 
        else:
            return None

# TODO test.
def copy_gb_data(ncbi_handle, acc_id_dict, records_path, file_type, 
                                                        verbose=False): 
    """Save retrieved records to file.""" 
    if file_type == "gb":
        record_parser = SeqIO.parse(ncbi_handle, "genbank")
       
        seqrecords = []
        for record in record_parser:
            accession = record.annotations["accessions"][0]
            phage_id = acc_id_dict[accession]
            record.name = phage_id
            seqrecords.append(record)

        ncbi_handle.close()
        fileio.write_seqrecord(seqrecords, "gb", records_path, verbose=verbose)

    elif file_type == "tbl":
        file_lines = ncbi_handle.readlines()

        feature_format = re.compile(">Feature ..\|\w+\..\|")
        accession_format = re.compile("\|(\w+)\..\|")
        
        file_handle = None
        for line in file_lines:
            if not re.match(feature_format, line) is None:
                accession_split = re.split(accession_format, line)
                accession = accession_split[1]
                phage_id = acc_id_dict[accession_split[1]]

                file_name = (f"{phage_id}.tbl") 
                file_path = records_path.joinpath(file_name)
                file_handle = file_path.open(mode="w")

                file_handle.write(line)
            else:
                if file_handle is None:
                    continue
                file_handle.write(line) 
 
        ncbi_handle.close()
