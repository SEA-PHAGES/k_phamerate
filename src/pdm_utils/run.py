"""Use this script to run all pipelines within the pipelines folder.
It verifies a valid pipeline is selected,
then passes all command line arguments to the main pipeline module.
"""
import argparse
import sys

from pdm_utils.pipelines.cdd import cdd_pp
from pdm_utils.pipelines.data_retrieval import retrieve_database_updates
from pdm_utils.pipelines.db_compare import compare_databases
from pdm_utils.pipelines.db_export import export_database
from pdm_utils.pipelines.db_freeze import freeze_database
from pdm_utils.pipelines.db_import import import_genome
from pdm_utils.pipelines.db_import import import_phage
from pdm_utils.pipelines.phamerate import phamerate


def main():
    """Verify a valid pipeline is selected and arguments provided are valid.

    The command line arguments are parsed and performs several basic
    checks on the arguments. Then they are passed to sub-functions to
    specifically validate the arguments based on the selected pipeline.
    """
    # Assumed command line arg structure:
    # python3 -m pdm_utils.run <pipeline> <additional args...>
    # sys.argv:      [0]            [1]         [2...]
    RUN_HELP = "Command line script to call a pdm_utils pipeline."
    VALID_PIPELINES = {
        "retrieve_data",
        "import",
        "import_dev",
        "cdd",
        "phamerate",
        "export",
        "compare",
        "database_to_file",
        "freeze"}
    PIPELINE_HELP = "Name of the pdm_utils pipeline to run."
    pipe_parser = argparse.ArgumentParser(description=RUN_HELP)
    pipe_parser.add_argument("pipeline", type=str,
                        choices=list(VALID_PIPELINES),
                        help=PIPELINE_HELP)
    args = pipe_parser.parse_args(sys.argv[1:2])
    if args.pipeline == "retrieve_data":
        retrieve_database_updates.main(sys.argv)
    # Note: import_phage is the legacy import script and will be deprecated.
    # Once import_genome is tested and operational, 'import' will call the
    # 'import_genome' module instead of the 'import_phage' module.
    elif args.pipeline == "import":
        import_phage.main(sys.argv)
    elif args.pipeline == "import_dev":
        import_genome.run_import(sys.argv)
    elif args.pipeline == "cdd":
        cdd_pp.main(sys.argv)
    elif args.pipeline == "phamerate":
        phamerate.main(sys.argv[sys.argv.index("phamerate")+1:])
    elif args.pipeline == "export":
        export_database.main(sys.argv)
    # TODO eventually 'database_to_file' will be merged into 'export' pipeline.
    elif args.pipeline == "database_to_file":
        pass
    elif args.pipeline == "freeze":
        freeze_database.main(sys.argv)
    else:
        compare_databases.main(sys.argv)
    print("Pipeline completed")


if __name__ == "__main__":
    main()
