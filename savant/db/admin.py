import os
import argparse
from sqlalchemy import Table
from savant import db
from savant.db import models

class UserError(Exception):
    pass

def setup_database(alembic_config_path=None, reset=False):
    """
    Initalize database tables if they do not yet exist
    """
    # migration settings file
    if alembic_config_path and not os.path.isfile(alembic_config_path):
        raise UserError("alembic file does not exist")

    if reset:
        db.Base.metadata.remove(Table("industry", db.Base.metadata))
        db.Base.metadata.drop_all(db.session.get_bind())
    db.Base.metadata.create_all(db.session.get_bind())


def main():
    """
    Command-line interface to SavantDB administrative tools
    """
    parser = argparse.ArgumentParser(description="SavantDB administrative tools")
    subparsers = parser.add_subparsers(title="subcommands")

    # Subparser 'setup-database'
    p = subparsers.add_parser("setup-database", help="initialize SavantDB tables if not exist")
    p.add_argument("-r", "--reset", dest="reset", action="store_true", help="reset db tables")
    p.add_argument("-c", "--alembic-config", metavar="ALEMBIC_CONFIG", dest="alembic_config_path", help="path to alembic.ini")
    p.set_defaults(func=setup_database)
    
    args = parser.parse_args()
    try:
        args.func(**{k: v for k, v in vars(args).items() if k not in ("func")})
    except UserError as e:
        parser.error(unicode(e))

if __name__ == "__main__":
    main()
