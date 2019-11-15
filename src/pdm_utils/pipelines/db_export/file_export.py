"""Functions for converting a local SQL database query for a selction of phages 
to formatted files"""
"""Pipeline for converting a database, filtered for some phages, and writing 
appropriate output files"""

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation, CompoundLocation
from pdm_utils.classes import genome, cds, mysqlconnectionhandler, filter
from pdm_utils.functions import flat_files, phamerator, basic
from functools import singledispatch
from typing import List, Dict
from pathlib import Path
from contextlib import contextmanager
import cmd, readline, os, sys, typing, argparse, csv


#Global file constant
file_format_choices = ["gb", "fasta", "clustal", "embl",
                       "fasta-2line", "fastq", "fastq-solexa", 
                       "fastq-illumina","ig", "igmt", "nexus", 
                       "phd", "phylip", "pir", "seqxml","sff", 
                       "stockholm", "tab", "qual"]

def run_file_export(unparsed_args_list):
    """Uses parsed args to run the entirety of the file export pipeline
    """ 

    selection_args = parse_export_select(unparsed_args_list) 
    sql_handle = establish_database_connection(selection_args.database)

    if not selection_args.interactive:
        if selection_args.csv_export:
            args = parse_csvx(unparsed_args_list) 

            filter_list = parse_phage_list_input(args.list_input)

            execute_file_export(sql_handle, args.export_path, args.folder_name,
                                phage_filter_list=filter_list,
                                verbose=args.verbose, csv_export=True)

        elif selection_args.db_export:
            args = parse_dbx(unparsed_args_list)

            if args.folder_name == None:
                args.folder_name = selection_args.database

            execute_file_export(sql_handle, args.export_path, args.folder_name,
                                verbose=args.verbose, db_export=True)
  
        elif selection_args.ffile_export:
            args = parse_ffx(unparsed_args_list)

            if args.folder_name == None:
                args.folder_name = selection_args.database

            filter_list = parse_phage_list_input(args.list_input)

            execute_file_export(sql_handle, args.export_path, args.folder_name,
                                phage_filter_list=filter_list,
                                verbose=args.verbose,
                                ffile_export=args.file_format)

        elif selection_args.multi_export:
            args = parse_multix(unparsed_args_list)

            if args.folder_name == None:
                args.folder_name = selection_args.database

            filter_list = parse_phage_list_input(args.list_input)

            execute_file_export(sql_handle, args.export_path, args.folder_name,
                                phage_filter_list=filter_list,
                                verbose=args.verbose, 
                                ffile_export=args.ffile_export,
                                csv_export=args.csv_export, 
                                db_export=args.db_export)

    else:
        pass
 
def execute_file_export(sql_handle, export_path, folder_name, 
                        phage_filter_list=[], verbose=False, 
                        csv_export=False, ffile_export=None, db_export=False):
    """Executes the entirety of the file export pipeline by calling its
       various functions

       :param file_format:
            Input a recognized SeqIO file format.
       :type file_format: str:
       :param database:
            Input the name of the local phameratory database.
       :type database: str:
       :param phage_filter_list:
            Input a list of names of phages.
       :type phage_filter_list: List[str]
       :param export_directory_path:
            Input the path for the created directory.
       :type export_path: Path:
       :param folder_name:
            Input the name for the created directory.
       :type export_directory_name: str:
       :param verbose:
            Input a toggle for optional printed statements.
       :type verbose: Boolean:
       :param csv_log:
            Input a toggle for an optional csv log.
       :type csv_log: Boolean:
       """
 
    if verbose:
        print("Retrieving database version...")
    db_version = retrieve_database_version(sql_handle)

    if db_export:
        if verbose:
            print("Writing SQL database file...")
        write_database(sql_handle, db_version["version"],
                        export_path, export_dir_name=folder_name)

    if csv_export:
        if verbose:
            print(f"Retrieving genomic data from {sql_handle.database}...")
        genomes = phamerator.parse_genome_data(
                          sql_handle,
                          phage_id_list=phage_filter_list,
                          phage_query="SELECT * FROM phage",
                          gene_query="SELECT * FROM gene")

        if verbose:
                print("Writing csv file...")
        write_csv(genomes, export_path, export_dir_name=folder_name, 
                      csv_name=f"{sql_handle.database}_v{db_version['version']}")

    if ffile_export != None:
        if verbose:
            print(f"Retrieving genomic data from {sql_handle.database}...")
        genomes = phamerator.parse_genome_data(
                                sql_handle,
                                phage_id_list=phage_filter_list,
                                phage_query="SELECT * FROM phage",
                                gene_query="SELECT * FROM gene")

        if verbose:
            print("Converting genomic data to SeqRecord format...")
        seqrecords = []
        for gnm in genomes:
            set_cds_seqfeatures(gnm)
            if verbose:
                print(f"Converting {gnm.name}")
            seqrecords.append(flat_files.genome_to_seqrecord(gnm))
        if verbose:
            print("Appending database version...")
        for record in seqrecords:
            append_database_version(record, db_version)

        write_seqrecord(seqrecords, 
                        ffile_export, 
                        export_path, 
                        export_dir_name=folder_name,
                        verbose=verbose)
             
def parse_export_select(unparsed_args_list):
    """
    Verifies the correct arguments are selected 
    and parses arguments to select pipeline of export.
    :param unparsed_args_list:
        Input a series of unparsed args
    :type unparsed_args_list: list[str]: 
    :return parsed_args:
        Returns an Argument Parser object
        containing attributes with the
        parsed arguments
    :type parsed_args: ArgumentParser:
    """ 
    EXPORT_SELECT_HELP = """
        Select a export pipeline option to export genomic data:
            -csv_export (-csvx)
            -ffile_export (-ffx)
            -db_export (-dbx)
            -multi_export (-multix)
        """
    DATABASE_HELP = "Name of the MySQL database to export from."
    CSV_EXPORT_HELP = """
            Export option to export a csv file 
            containing information about selected genomes.
            """
    DATABASE_EXPORT_HELP = """
            Export option to dump the current database
            into a .sql file and its version into a .version file.
            """
    FORMATTED_FILE_EXPORT_HELP = """
            Export option to export formatted files containing
            information about individual genomes.
            """ 
    MULTIPLE_EXPORT_HELP = """
            Powerful export option that allows for 
            export of more than one or all export options.
            """
    INTERACTIVE_HELP = """
        Export option that enables full interactive walkthrough export.
        """
 
    export_select = argparse.ArgumentParser(description = EXPORT_SELECT_HELP)
    export_select.add_argument("database", type=str,
                               help=DATABASE_HELP, default=None)
                                
    export_options = export_select.add_mutually_exclusive_group(required=True)
    export_options.add_argument("-csvx", "--csv_export",
                                help=CSV_EXPORT_HELP, 
                                action="store_true")
    export_options.add_argument("-dbx", "--db_export", 
                                help=DATABASE_EXPORT_HELP,
                                action="store_true")
    export_options.add_argument("-ffx", "--ffile_export", 
                                help=FORMATTED_FILE_EXPORT_HELP,
                                action="store_true")
    export_options.add_argument("-multix", "--multi_export",
                                help=MULTIPLE_EXPORT_HELP,
                                action="store_true")
    export_options.add_argument("-i", "--interactive",
                                 default=False,
                                 help=INTERACTIVE_HELP,
                                 action='store_true')

    parsed_args = export_select.parse_args(unparsed_args_list[2:4])
    return parsed_args

def parse_multix(unparsed_args_list):
    """
    Verifies the correct arguments are selected 
    and parses arguments for multiple pipeline export.
    :param unparsed_args_list:
        Input a series of unparsed args
    :type unparsed_args_list: list[str]: 
    :return parsed_args:
        Returns an Argument Parser object
        containing attributes with the
        parsed arguments
    :type parsed_args: ArgumentParser:
    """
    MULTIPLE_EXPORT_HELP = """
        Powerful export option that allows for 
        export of more than one or all export options.
        """
    IMPORT_TABLE_HELP = """
        Genome selection input option that imports genomes from a csv file.
            Follow selection argument with path to the 
            csv file containing the names of each genome in the first column.
        """
    SINGLE_GENOMES_HELP = """
        Genome selection input option that imports genomes from cmd line input.
            Follow selection argument with space separated
            names of genomes in the database.
        """
    ALL_HELP = """
        Genome selection input option that selects all genomes.
            Set as default option.
        """
    VERBOSE_HELP = """
        Export option that enables progress print statements.
        """
    EXPORT_DIRECTORY_HELP = """
        Export option to change the path 
        of the directory where the exported files are stored.
            Follow selection argument with the path to the
            desired export directory.
        """
    FOLDER_NAME_HELP = """
        Export option to change the name 
        of the directory where the exported files are stored.
            Follow selection argument with the desired name.
        """
    CSV_EXPORT_HELP = """
        Export option to export a csv file 
        containing information about selected genomes.
        """
    FORMATTED_FILE_EXPORT_HELP = """
        Export option to export formatted files containing
        information about individual genomes.
        """ 
    DATABASE_EXPORT_HELP = """
        Export option to dump the current database
        into a .sql file and its version into a .version file.
        """

    multix_parser = argparse.ArgumentParser(description = MULTIPLE_EXPORT_HELP)

    phage_list = multix_parser.add_mutually_exclusive_group()
    phage_list.add_argument("-tin", "--import_table",
                                       nargs=1, type=convert_file_path,
                                       dest="list_input",
                                       help=IMPORT_TABLE_HELP)
    phage_list.add_argument("-sgin", "--single_genomes",
                                       nargs='+', type=str,
                                       dest="list_input",
                                       help=SINGLE_GENOMES_HELP)
    phage_list.add_argument("-a", "--all",
                                       action ='store_const',
                                       dest="list_input", const=[],
                                       help=ALL_HELP)

    multix_parser.add_argument("-v", "--verbose",
                               default=False,
                               help=VERBOSE_HELP,
                               action='store_true')
    multix_parser.add_argument("-pth", "--export_path",
                        default=Path.cwd(), type=convert_dir_path,
                        help=EXPORT_DIRECTORY_HELP) 
    multix_parser.add_argument("-name", "--folder_name",
                        default="Export", type=str, 
                        help=FOLDER_NAME_HELP)

    multix_parser.add_argument("-ffx", "--ffile_export", type=str,
                        default=None, choices=file_format_choices,
                        help=FORMATTED_FILE_EXPORT_HELP)
    multix_parser.add_argument("-csvx", "--csv_export",
                        help=CSV_EXPORT_HELP, action="store_true")
    multix_parser.add_argument("-dbx", "--db_export", 
                        help=DATABASE_EXPORT_HELP, action="store_true")

    parsed_args = multix_parser.parse_args(unparsed_args_list[4:])
    return parsed_args

def parse_csvx(unparsed_args_list):
    """
    Verifies the correct arguments are selected 
    and parses arguments for csv export.
    :param unparsed_args_list:
        Input a series of unparsed args
    :type unparsed_args_list: list[str]: 
    :return parsed_args:
        Returns an Argument Parser object
        containing attributes with the
        parsed arguments
    :type parsed_args: ArgumentParser:
    """
    CSV_EXPORT_HELP = """
        Export option to export a csv file 
        containing information about selected genomes.
        """ 
    IMPORT_TABLE_HELP = """
        Genome selection input option that imports genomes from a csv file.
            Follow selection argument with path to the 
            csv file containing the names of each genome in the first column.
        """
    SINGLE_GENOMES_HELP = """
        Genome selection input option that imports genomes from cmd line input.
            Follow selection argument with space separated
            names of genomes in the database.
        """
    ALL_HELP = """
        Genome selection input option that selects all genomes.
            Set as default option.
        """
    VERBOSE_HELP = """
        Export option that enables progress print statements.
        """
    EXPORT_DIRECTORY_HELP = """
        Export option to change the path 
        of the directory where the exported files are stored.
            Follow selection argument with the path to the
            desired export directory.
        """
    FOLDER_NAME_HELP = """
        Export option to change the name 
        of the directory where the exported files are stored.
            Follow selection argument with the desired name.
        """
    csvx_parser = argparse.ArgumentParser(description=CSV_EXPORT_HELP)

    phage_list = csvx_parser.add_mutually_exclusive_group()
    phage_list.add_argument("-tin", "--import_table",
                                       nargs=1, type=convert_file_path,
                                       dest="list_input",
                                       help=IMPORT_TABLE_HELP)
    phage_list.add_argument("-sgin", "--single_genomes",
                                       nargs='+', type=str,
                                       dest="list_input",
                                       help=SINGLE_GENOMES_HELP)
    phage_list.add_argument("-a", "--all",
                                       action ='store_const',
                                       dest="list_input", const=[],
                                       help=ALL_HELP)

    csvx_parser.add_argument("-v", "--verbose",
                        default=False,
                        help=VERBOSE_HELP,
                        action='store_true') 
    csvx_parser.add_argument("-pth", "--export_path",
                        default=Path.cwd(), type=convert_dir_path,
                        help=EXPORT_DIRECTORY_HELP) 
    csvx_parser.add_argument("-name", "--folder_name",
                             default="Export", type=str, 
                             help=FOLDER_NAME_HELP)
    
    parsed_args = csvx_parser.parse_args(unparsed_args_list[4:])
    return parsed_args

def parse_dbx(unparsed_args_list):
    """
    Verifies the correct arguments are selected 
    and parses arguments for database export.
    :param unparsed_args_list:
        Input a series of unparsed args
    :type unparsed_args_list: list[str]: 
    :return parsed_args:
        Returns an Argument Parser object
        containing attributes with the
        parsed arguments
    :type parsed_args: ArgumentParser:
    """
    DATABASE_EXPORT_HELP = """
        Export option to dump the current database
        into a .sql file and its version into a .version file.
        """
    VERBOSE_HELP = """
        Export option that enables progress print statements.
        """
    INTERACTIVE_HELP = """
        Export option that enables full interactive walkthrough export.
        """
    EXPORT_DIRECTORY_HELP = """
        Export option to change the path 
        of the directory where the exported files are stored.
            Follow selection argument with the path to the
            desired export directory.
        """
    FOLDER_NAME_HELP = """
        Export option to change the name 
        of the directory where the exported files are stored.
            Follow selection argument with the desired name.
        """
    dbx_parser = argparse.ArgumentParser(description = DATABASE_EXPORT_HELP)
  
    dbx_parser.add_argument("-v", "--verbose",
                        default=False,
                        help=VERBOSE_HELP,
                        action='store_true')
    dbx_parser.add_argument("-pth", "--export_path",
                        default=Path.cwd(), type=convert_dir_path,
                        help=EXPORT_DIRECTORY_HELP) 
    dbx_parser.add_argument("-name", "--folder_name",
                        default="Export", type=str, 
                        help=FOLDER_NAME_HELP)
    
    parsed_args = dbx_parser.parse_args(unparsed_args_list[4:])
    return parsed_args
    
def parse_ffx(unparsed_args_list):
    """
    Verifies the correct arguments are selected 
    and parses arguments for formatted file export.
    :param unparsed_args_list:
        Input a series of unparsed args
    :type unparsed_args_list: list[str]: 
    :return parsed_args:
        Returns an Argument Parser object
        containing attributes with the
        parsed arguments
    :type parsed_args: ArgumentParser:
    """
    FORMATTED_FILE_EXPORT_HELP = """
        Export option to export formatted files containing
        information about individual genomes.
        """   
    FILE_FORMAT_HELP = """
        Positional argument specifying the format of the file to export
        """
        
    IMPORT_TABLE_HELP = """
        Genome selection input option that imports genomes from a csv file.
            Follow selection argument with path to the 
            csv file containing the names of each genome in the first column.
        """
    SINGLE_GENOMES_HELP = """
        Genome selection input option that imports genomes from cmd line input.
            Follow selection argument with space separated
            names of genomes in the database.
        """
    ALL_HELP = """
        Genome selection input option that selects all genomes.
            Set as default option.
        """
    VERBOSE_HELP = """
        Export option that enables progress print statements.
        """
    INTERACTIVE_HELP = """
        Export option that enables full interactive walkthrough export.
        """
    EXPORT_DIRECTORY_HELP = """
        Export option to change the path 
        of the directory where the exported files are stored.
            Follow selection argument with the path to the
            desired export directory.
        """
    FOLDER_NAME_HELP = """
        Export option to change the name 
        of the directory where the exported files are stored.
            Follow selection argument with the desired name.
        """

    ffx_parser = argparse.ArgumentParser(
                            description=FORMATTED_FILE_EXPORT_HELP)

    ffx_parser.add_argument("file_format", help=FILE_FORMAT_HELP, 
                            choices=file_format_choices)
    phage_list = ffx_parser.add_mutually_exclusive_group()
    phage_list.add_argument("-tin", "--import_table",
                                       nargs=1, type=convert_file_path,
                                       dest="list_input",
                                       help=IMPORT_TABLE_HELP)
    phage_list.add_argument("-sgin", "--single_genomes",
                                       nargs='+', type=str,
                                       dest="list_input",
                                       help=SINGLE_GENOMES_HELP)
    phage_list.add_argument("-a", "--all",
                                       action ='store_const',
                                       dest="list_input", const=[],
                                       help=ALL_HELP)

    ffx_parser.add_argument("-v", "--verbose",
                        default=False,
                        help=VERBOSE_HELP,
                        action='store_true') 
    ffx_parser.add_argument("-pth", "--export_path",
                        default=Path.cwd(), type=convert_dir_path,
                        help=EXPORT_DIRECTORY_HELP) 
    ffx_parser.add_argument("-name", "--folder_name",
                        default="Export", type=str, 
                        help=FOLDER_NAME_HELP)
    
    parsed_args = ffx_parser.parse_args(unparsed_args_list[4:])
    return parsed_args

def convert_path(path: str):
    """
    Function to convert a string to a working Path object
    :param path:
        Input a string to be converted into a Path object.
    :type path: str
    :return path_object:
    Returns a path object from the inputted
    :type path_object: Path
    """
    path_object = Path(path)
    if "~" in path:
        path_object = path_object.expanduser()

    if path_object.exists():
        return path_object
    elif path_object.resolve().exists():
        path_object = path_object.resolve()
    
    print("String input failed to be converted to a working Path object " \
          "Path does not exist")

    raise ValueError 

def convert_dir_path(path: str):
    """
    Helper function to convert a string to a working Path object
    :param path:
        Input a string to be converted into a Path object.
    :type path: str
    :return path_object:
        Returns a path object directing to a directory.
    :type path_object: Path
    """

    path_object = convert_path(path)

    if path_object.is_dir():
        return path_object
    else:
        print("Path input does not direct to a folder")
        raise ValueError

def convert_file_path(path: str):
    """
    Helper function to convert a string to a working Path object
    :param path:
        Input a string to be converted into a Path object.
    :type path: str
    :return path_object:
        Returns a path object directing to a file.
    :type path_object: Path
    """
    path_object = convert_path(path)

    if path_object.is_file():
        return path_object
    else:
        print("Path input does not direct to a file")
        raise ValueError

@singledispatch
def parse_phage_list_input(phage_list_input): 
    """Helper function to populate the filter list for a SQL query
    :param phage_list_input:
        Input a list of phage names.
    :type phage_list_input: list[str]
    """

    print("Phage list input for database query is not a supported type")
    raise TypeError

@parse_phage_list_input.register(Path)
def _(phage_list_input):
    phage_list = []
    with open(phage_list_input, newline = '') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter = ",", quotechar = '|')
        for name in csv_reader:
            phage_list.append(name[0])
    return phage_list

@parse_phage_list_input.register(list)
def _(phage_list_input):
    return phage_list_input

def establish_database_connection(database_name: str):
    """Creates a mysqlconnectionhandler object 
    and populates its credentials

    :param tag database_name:
        Input SQL database name.
    "type database_name: str
    """

    if not isinstance(database_name, str):
        print("establish_database_connection requires string input")
        raise TypeError
    sql_handle = mysqlconnectionhandler.MySQLConnectionHandler()
    sql_handle.database = database_name
    sql_handle.get_credentials()
    try:
        sql_handle.open_connection()
    except:
        print(f"SQL connection to database {database_name}"
            "with username and password failed")
        raise RuntimeError 

    return sql_handle
    
def set_cds_seqfeatures(phage_genome: genome.Genome):
    """Helper function that queries for and returns 
    cds data from a SQL database for a specific phage

    :param phage_genome:
        Input a genome object to query cds data for.
    :type phage_genome: genome
    :param sql_database_handle:
        Input a mysqlconnectionhandler object.
    :type sql_database_handle: mysqlconnectionhandler
    """

    try:
        def _sorting_key(cds_feature): return cds_feature.left
        phage_genome.cds_features.sort(key=_sorting_key)
    except:
        if phage_genome == None:
            raise TypeError
        print("Genome cds features unable to be sorted")
        pass
    for cds_feature in phage_genome.cds_features:
        cds_feature.set_seqfeature()

def retrieve_database_version(sql_handle):
    """Helper function that queries a SQL database
    for the database version and schema version

    :param sql_database_handle:
        Input a mysqlconnectionhandler object.
    :type sql_database_handle: mysqlconnectionhandler
    :returns:
        database_versions_list(dictionary) is a dictionary
        of size 2 that contains values tied to keys
        "version" and "schema_version"
    """

    database_versions_list = phamerator.retrieve_data(
            sql_handle, query='SELECT * FROM version')
    return database_versions_list[0]

def append_database_version(genome_seqrecord: SeqRecord, version_data: Dict):
    """Helper function that appends the working database version 
    in a comment within a SeqFeature annotation

    :param genome_seqfeature:
        Input a SeqRecord object generated from the working
        SQL database.
    :type genome_seqfeature: SeqRecord
    :param version_data:
        Input a version data dictionary parsed from a SQL database.
    :type version_data: dictionary
    """

    if len(version_data) < 2:
        print("Version data dictionary "
        "containing SQL database version "
        "data does not contain enough values")
        raise ValueError
    try:
        genome_seqrecord.annotations["comment"] =\
                genome_seqrecord.annotations["comment"] + (
                    "Database Version: {}; Schema Version: {}".format(
                                        version_data["version"], 
                                        version_data["schema_version"]),)
    except:
        if isinstance(genome_seqrecord, SeqRecord):
            raise ValueError

        elif genome_seqrecord == None:
            raise TypeError
        raise

def write_seqrecord(seqrecord_list: List[SeqRecord], 
                           file_format: str,
                           export_path: Path, 
                           export_dir_name="export",
                           verbose=False):
    """Outputs files with a particuar format from a SeqRecord list

    :param seq_record_list:
        Input a list of SeqRecords.
    :type seq_record_list: SeqRecord[]
    :param file_format:
        Input SeqIO file output format.
    :type file_format: str
    :param export_path:
        Input the path for the placement of the directory
        of exported files.
    :type input_path: Path
    :param verbose:
        Input a boolean to represent the verbocity of
        the file export script.
    :type verbose: Boolean
    """

    if verbose:
        print("Resolving export path...")
    export_path = export_path.resolve()
    if not export_path.exists():
        print("Path parameter passed to seqfeature_file_output\
            is not a valid path")
        raise ValueError

    try: 
        export_path = export_path.joinpath(export_dir_name)
        if verbose:
            print("Resolving current export directory status...")
        if not export_path.is_dir():
            export_path.mkdir()
    except:
        print("Mkdir function failed to" 
              f" create database_export_output directory in {export_path}")
        raise ValueError 
    
    if verbose:
        print("Writing selected data to files...")
    for record in seqrecord_list:
        if verbose:
            print(f"Writing {record.name}")
        output_dir = f"{record.name}.{file_format}"
        output_path = export_path.joinpath(output_dir)
        output_handle = output_path.open(mode='w')
        SeqIO.write(record, output_handle, file_format)
        output_handle.close()

def write_csv(genome_list, export_path, export_dir_name="export", 
                                        csv_name="database"):
    """Writes a formatted csv file from genome objects"""

    export_path = export_path.joinpath(export_dir_name)

    if not export_path.exists():
        export_path.mkdir()

    csv_path = Path(os.path.join(export_path, f"{csv_name}.csv"))
    csv_version = 1

    while(csv_path.exists()):
        csv_version += 1
        csv_path = export_path.joinpath(f"{csv_name}{csv_version}.csv")
 
    csv_data = []
    csv_data.append(   ["PhageID",
                        "Accession",
                        "Name",
                        "HostStrain",
                        "SequenceLength",
                        "DateLastModified",
                        "Notes",
                        "GC",
                        "Cluster",
                        "Subcluster",
                        "Status",
                        "RetrieveRecord",
                        "AnnotationAuthor",])
    for gnm in genome_list:
        csv_data.append([gnm.id,
                         gnm.accession,
                         gnm.name,
                         gnm.host_genus,
                         gnm.length,
                         gnm.date,
                         gnm.description,
                         gnm.gc,
                         gnm.cluster,
                         gnm.subcluster,
                         gnm.annotation_status,
                         gnm.retrieve_record,
                         gnm.annotation_author])
    csv_path.touch()
    with open(csv_path, 'w', newline="") as csv_file:
        csvwriter = csv.writer(csv_file, delimiter=",", 
                               quotechar = "|", 
                               quoting = csv.QUOTE_MINIMAL)
        for row in csv_data:
            csvwriter.writerow(row)

def write_database(sql_handle, version, export_path, 
                    export_dir_name="export"):
    
    export_path = export_path.joinpath(export_dir_name)

    if not export_path.exists():
        export_path.mkdir()

    sql_path = export_path.joinpath(f"{sql_handle.database}_v{version}.sql")
   
    os.system(f"mysqldump -u {sql_handle._username} -p{sql_handle._password} "
              f"--skip-comments {sql_handle.database} > {str(sql_path)}")
    
    version_path = sql_path.with_name(f"{sql_handle.database}_v{version}.version")
    version_path.touch()
    version_path.write_text(f"{version}")

def main(args):
    """Function to initialize file export"""
    run_file_export(args)

class Cmd_Export(cmd.Cmd):

    def __init__(self, file_format="gb",database=None,
                 phage_filter_list=[], sql_handle=None,
                 export_directory_name="file_export",
                 export_directory_path = Path.cwd()):

        super(Cmd_Export, self).__init__()

        self.file_format = file_format
        self.database = database
        self.phage_filter_list = phage_filter_list
        self.sql_handle = sql_handle
        self.directory_name = export_directory_name
        self.directory_path = export_directory_path
        self.csv_toggle = False

        self.intro =\
        """---------------Hatfull Helper's File Export---------------
        Type help or ? to list commands.\n"""
        self.prompt = "(database) (export)user@localhost: "
        self.data = None

    def preloop(self):
        
        if self.database == None:
            print("---------------------Database Login ---------------------")
            self.database = input("MySQL database: ")

        if self.sql_handle == None or \
           self.sql_handle.database != self.database:  
            self.sql_handle = establish_database_connection(self.database)

        self.prompt = "({}) (export){}@localhost: ".\
                format(self.database, self.sql_handle._username)

    def do_search(self, *args):
        """Filters and queries database for genomes.
        """
        db_filter = filter.Filter(self.database, self.sql_handle)
        interactive_filter = filter.Cmd_Filter(
                db_filter=db_filter, sql_handle=self.sql_handle)
        interactive_filter.cmdloop()
        self.phage_filter_list = interactive_filter.data

    def do_folder(self, *args):
        """Selects options for current folder
        FOLDER OPTIONS: Format, Path, Name, Export, Log
        """

        options = ["format", "path", "name", "export", "log"]
        option = args[0].lower()

        if option in options:
            if option == "format":
                self.folder_format()
            elif option == "path":
                self.folder_directory_path()
            elif option == "name":
                self.folder_directory_name()
            elif option =="export":
                self.folder_export()
            elif option == "log":
                if self.csv_toggle:
                    print("Csv logging off. \n")
                    self.csv_toggle = False
                else:
                    print("Csv logging on. \n")
                    self.csv_toggle = True
        else:
            print("""Folder command option not supported
            FOLDER OPTIONS: Format, Path, Name, Export, Log
            """)

    def folder_format(self):
        """Sets the current file format for genome export
        """

        format = input("File Format: ")
        if format in file_export_choices:
            self.file_format = format
            print("\
                    Changed format to {}.\n".format(self.file_format))
        else:
            print("File format not supported.\n")
        
    def folder_directory_path(self):
        """Sets the export directory name for genome export
        USAGE: format
        """
        
        path = Path(input("Export Directory Path: "))
        if path.resolve():
            self.directory_path = path
        else:
            print("\
                    Path not found.")

    def folder_directory_name(self):
        """Sets the export directory name for genome export
        USAGE: format
        """

        self.directory_name = input("Export Directory Name: ") 

    def folder_export(self, *args):
        """Exit interface and finish exporting files
        USAGE: export
        """
        print("\
                Initiating Export...\n")
        execute_file_export(self.file_format, self.sql_handle,
                                self.phage_filter_list, self.directory_path,
                                self.directory_name, 
                                verbose=False, csv_log=False)

    def do_clear(self, *args):        
        """Clears display terminal
        USAGE: clear
        """

        os.system('cls' if os.name == 'nt' else 'clear')
        print(self.intro)
       
    def do_exit(self, *args):
        """Exits program entirely without returning values
        USAGE: exit
        """
        print("       Exiting...\n")

        sys.exit(1)

if __name__ == "__main__":
   
    args = sys.argv
    args.insert(0, "blank_argument")
    main(args)
