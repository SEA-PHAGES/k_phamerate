import argparse
import logging
import os
import pathlib
import platform
import shlex
import sys
from subprocess import Popen, PIPE

from Bio.Blast import NCBIXML
from Bio.Blast.Applications import NcbirpsblastCommandline

import pdm_utils
from pdm_utils.constants import constants
from pdm_utils.functions import basic
from pdm_utils.functions import mysqldb
from pdm_utils.functions.basic import expand_path
from pdm_utils.functions.parallelize import *

# SQL QUERIES
GET_GENES_FOR_CDD = (
    "SELECT GeneID, Translation FROM gene WHERE DomainStatus = 0")
GET_UNIQUE_HIT_IDS = "SELECT HitID FROM domain"

# SQL COMMANDS
INSERT_INTO_DOMAIN = """INSERT IGNORE INTO domain (HitID, DomainID, Name, Description) VALUES ("{}", "{}", "{}", "{}")"""
INSERT_INTO_GENE_DOMAIN = """INSERT IGNORE INTO gene_domain (GeneID, HitID, Expect, QueryStart, QueryEnd) VALUES ("{}", "{}", {}, {}, {})"""
UPDATE_GENE = "UPDATE gene SET DomainStatus = 1 WHERE GeneID = '{}'"

# MISC
VERSION = pdm_utils.__version__
RESULTS_FOLDER = f"{constants.CURRENT_DATE}_cdd"

# LOGGING
# Add a logger named after this module. Then add a null handler, which
# suppresses any output statements. This allows other modules that call this
# module to define the handler and output formats. If this module is the
# main module being called, the top level main function configures
# the root logger and primary file handle.
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def setup_argparser():
    """
    Builds argparse.ArgumentParser for this script
    :return:
    """
    # Pipeline description
    description = (
        "Uses rpsblast to search the NCBI conserved domain database "
        "for significant domain hits in all new proteins of a "
        "MySQL database.")
    output_folder_help = "Directory where log data can be generated."
    log_file_help = "Name of the log file generated."

    # Initialize parser and add arguments
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("db", type=str,
                        help="name of database to phamerate")
    parser.add_argument("dir", type=str,
                        help="path to local directory housing CDD database")
    parser.add_argument("--threads", default=mp.cpu_count(), type=int,
                        help="number of concurrent CDD searches to run")
    parser.add_argument("--evalue", default=0.001, type=float,
                        help="evalue cutoff for rpsblast hits")
    parser.add_argument("--tmp_dir", default="/tmp/cdd", type=str,
                        help="path to temporary directory for file I/O")
    parser.add_argument("--rpsblast", default="", type=str,
                        help="path to rpsblast(+) binary")
    parser.add_argument("--output_folder", type=pathlib.Path,
        default=pathlib.Path("/tmp/"), help=output_folder_help)
    parser.add_argument("--log_file", type=str, default="find_domains.log",
        help=log_file_help)
    return parser


def make_tempdir(tmp_dir):
    """
    Uses pdm_utils.functions.basic.expand_path to expand TMP_DIR; then
    checks whether tmpdir exists - if it doesn't, uses os.makedirs to
    make it recursively.
    :param tmp_dir: location where I/O should take place
    :return:
    """
    try:
        path = expand_path(tmp_dir)
        # If the path doesn't exist yet
        if not os.path.exists(path):
            # Make it recursively
            os.makedirs(path)
    except OSError as err:
        print(f"Error {err.args[0]}: {err.args[1]}")


def search_and_process(rpsblast, cdd_name, tmp_dir, evalue,
                       geneid, translation):
    """
    Uses rpsblast to search indicated gene against the indicated CDD
    :param rpsblast: path to rpsblast binary
    :param cdd_name: CDD database path/name
    :param tmp_dir: path to directory where I/O will take place
    :param evalue: evalue cutoff for rpsblast
    :param geneid: name of the gene to query
    :param translation: protein sequence for gene to query
    :return: results
    """
    # Setup I/O variables
    i = "{}/{}.txt".format(tmp_dir, geneid)
    o = "{}/{}.xml".format(tmp_dir, geneid)

    # Write the input file
    with open(i, "w") as fh:
        fh.write(">{}\n{}".format(geneid, translation))

    # Setup and run the rpsblast command
    rps_command = NcbirpsblastCommandline(cmd=rpsblast, db=cdd_name,
                                          query=i, out=o, outfmt=5,
                                          evalue=evalue)
    rps_command()

    # Process results into a single list
    results = []

    with open(o, "r") as fh:
        for record in NCBIXML.parse(fh):
            # Only need to process if there are record alignments
            if record.alignments:
                for align in record.alignments:
                    for hsp in align.hsps:
                        if hsp.expect <= evalue:
                            align.hit_def = align.hit_def.replace("\"", "\'")

                            des_list = align.hit_def.split(",")
                            if len(des_list) == 1:
                                description = des_list[0].strip()
                                domain_id = None
                                name = None
                            elif len(des_list) == 2:
                                domain_id = des_list[0].strip()
                                description = des_list[1].strip()
                                name = None
                            else:
                                domain_id = des_list[0].strip()
                                name = des_list[1].strip()
                                description = ",".join(des_list[2:]).strip()

                            # Try to put domain into domain table
                            results.append(INSERT_INTO_DOMAIN.format(
                                align.hit_id, domain_id, name, description))

                            # Try to put this hit into gene_domain table
                            results.append(INSERT_INTO_GENE_DOMAIN.format(
                                geneid, align.hit_id, float(hsp.expect),
                                int(hsp.query_start), int(hsp.query_end)))

    # Update this gene's DomainStatus to 1
    results.append(UPDATE_GENE.format(geneid))
    return results


def learn_cdd_name(cdd_dir):
    cdd_files = os.listdir(cdd_dir)
    cdd_files = [os.path.join(cdd_dir, x.split(".")[0]) for x in cdd_files]
    file_set = set(cdd_files)
    if len(file_set) == 1:
        cdd_name = cdd_files[0]
    else:
        cdd_name = ""
    return cdd_name


def main(argument_list):
    """
    :param argument_list:
    :return:
    """
    # Setup argument parser
    cdd_parser = setup_argparser()

    # Use argument parser to parse argument_list
    args = cdd_parser.parse_args(argument_list)

    # Store arguments in more easily accessible variables
    database = args.db
    cdd_dir = expand_path(args.dir)
    cdd_name = learn_cdd_name(cdd_dir)
    threads = args.threads
    evalue = args.evalue
    rpsblast = args.rpsblast
    tmp_dir = args.tmp_dir
    output_folder = args.output_folder
    log_file = args.log_file

    output_folder = basic.set_path(output_folder, kind="dir", expect=True)
    results_folder = pathlib.Path(RESULTS_FOLDER)
    results_path = basic.make_new_dir(output_folder, results_folder,
                                      attempt=10)
    if results_path is None:
        print("Unable to create output_folder.")
        sys.exit(1)

    log_file = pathlib.Path(results_path, log_file)

    # Set up root logger.
    logging.basicConfig(filename=log_file, filemode="w",
                        level=logging.DEBUG,
                        format="pdm_utils find_domains: %(levelname)s: %(message)s")
    logger.info(f"pdm_utils version: {VERSION}")
    logger.info(f"CDD run date: {constants.CURRENT_DATE}")
    logger.info(f"Command line arguments: {' '.join(argument_list)}")
    logger.info(f"Results directory: {results_path}")

    # Early exit if either 1) cdd_name == "" or 2) no rpsblast given and we are
    # unable to find one
    if cdd_name == "":
        msg = (f"Unable to learn CDD database name. Make sure the files in "
              f"{cdd_dir} all have the same basename.")
        logger.error(msg)
        print(msg)
        return

    # Get the rpsblast command and path.
    if rpsblast == "":
        command = get_rpsblast_command()
        rpsblast = get_rpsblast_path(command)

    engine = mysqldb.connect_to_db(database)
    logger.info("Command line arguments verified.")

    # Get gene data that needs to be processed
    # in dict format where key = column name, value = stored value.
    # result = engine.execute(GET_GENES_FOR_CDD)
    cdd_genes = mysqldb.query_dict_list(engine, GET_GENES_FOR_CDD)
    msg = f"{len(cdd_genes)} genes to search for conserved domains..."
    logger.info(msg)
    print(msg)

    # Only run the pipeline if there are genes returned that need it
    if len(cdd_genes) > 0:
        log_gene_ids(cdd_genes)

        # Create temp_dir
        make_tempdir(tmp_dir)

        # Build jobs list
        jobs = []
        for cdd_gene in cdd_genes:
            jobs.append((rpsblast, cdd_name, tmp_dir, evalue,
                         cdd_gene["GeneID"], cdd_gene["Translation"]))

        results = parallelize(jobs, threads, search_and_process)
        print("\n")
        insert_domain_data(engine, results)
        engine.dispose()
    return


def get_rpsblast_command():
    """Determine rpsblast+ command based on operating system."""
    # See if we're running on a Mac
    if platform.system() == "Darwin":
        msg = "Detected MacOS operating system..."
        logger.info(msg)
        print(msg)
        command = shlex.split("which rpsblast")
    # Otherwise see if we're on a Linux machine
    elif platform.system() == "Linux":
        msg = "Detected Linux operating system..."
        logger.info(msg)
        print(msg)
        command = shlex.split("which rpsblast+")
    # Windows or others - unsupported, leave early
    else:
        msg = (f"Unsupported system '{platform.system()}'; cannot run "
              f"find_domains pipeline.")
        logger.error(msg)
        print(msg)
        sys.exit(1)
    return command


def get_rpsblast_path(command):
    """Determine rpsblast+ binary path."""

    # If we didn't exit, we have a command.
    # Run it, and PIPE stdout into rpsblast_path
    with Popen(args=command, stdout=PIPE) as proc:
        rpsblast = proc.stdout.read().decode("utf-8").rstrip("\n")

    # If empty string, rpsblast not found in globally
    # available executables, otherwise proceed with value.
    if rpsblast == "":
        msg = ("No rpsblast binary found. "
              "If you have rpsblast on your machine, please try "
              "again with the '--rpsblast' flag and provide the "
              "full path to your rpsblast binary.")
        logger.error(msg)
        print(msg)
        sys.exit(1)
    else:
        msg = f"Found rpsblast binary at '{rpsblast}'..."
        logger.info(msg)
        print(msg)
        return rpsblast


def log_gene_ids(cdd_genes):
    """Record names of the genes processed for reference."""
    batch_indices = basic.create_indices(cdd_genes, 20)
    for indices in batch_indices:
        genes_subset = cdd_genes[indices[0]: indices[1]]
        gene_ids = []
        for gene in genes_subset:
            gene_ids.append(gene["GeneID"])
        logger.info("; ".join(gene_ids))


def insert_domain_data(engine, results):
    """Attempt to insert domain data into the database."""
    rolled_back = 0
    for result in results:
        exe_result = mysqldb.execute_transaction(engine, result)
        if exe_result == 1:
            msg = "One of the following statements caused a rollback:"
            logger.warning(msg)
            print(msg)
            for stmt in result:
                logger.warning(stmt)
            logger.warning("Attempting to resolve possible '%' error(s).")

            # Some CDD descriptions contain '%', which throws an error
            # when SQLAlchemy's engine.Connection.execute() is used.
            # The string gets passed to a pymysql.cursor function which
            # interprets the % as a string formatting operator,
            # and since there is no value to insert and format,
            # the MySQL statement fails and the
            # entire transactions is rolled back.
            # For these edge cases, one way around this is to
            # attempt to replace all '%' with '%%'.
            # SQLAlchemy provides several different ways to
            # implement changes to the database, and another strategy
            # is likely to get around this problem.
            index = 0
            while index < len(result):
                statement = result[index]
                statement = statement.replace("%", "%%")
                result[index] = statement
                index += 1
            exe_result = mysqldb.execute_transaction(engine, result)
            if exe_result == 0:
                logger.info("'%' replacement resolved the error(s).")
            else:
                logger.error("Unable to resolve error.")
        rolled_back += exe_result

    if rolled_back > 0:
        msg = (f"\n\n\nError executing {rolled_back} transaction(s). "
              "Unable to complete pipeline. "
              "Some genes may still contain unidentified domains.")
        logger.error(msg)
    else:
        msg = "All genes successfully searched for conserved domains."
        logger.info(msg)
        print("\n\n\n" + msg)