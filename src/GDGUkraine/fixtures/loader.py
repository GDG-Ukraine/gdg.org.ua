#!/usr/bin/env python3

import argparse
import importlib
import yaml

from blueberrypy.config import BlueberryPyConfiguration

from sqlalchemy import engine_from_config, pool
from sqlalchemy.orm import sessionmaker


def import_class(what):
    """Import a class by given full name.

    Args:
        what (str): a string with full classname to import
    Return:
        (type): a class which has been imported
    """
    modulename, classname = what.rsplit('.', 1)
    module = importlib.import_module(modulename)
    return getattr(module, classname)


def load_fixtures(filepath):
    """Loads fixtures from given file.

    Args:
        filepath (str): path to file from which fixtures should be imported
    Returns:
        (list): list of instantiated objects
    """
    models = []
    with open(filepath, 'r') as data_file:
        data = yaml.safe_load(data_file)
        for cls, descriptions in data.items():
            model_cls = import_class(cls)
            for description in descriptions:
                models.append(model_cls(**description))
    return models


def _parse_args():
    """Parse and return commandline args."""
    parser = argparse.ArgumentParser(description='Pre-fill the DB with fixtures.')
    parser.add_argument('--env', dest='environment', default='dev',
                        help='Environment for picking the config (default: dev)')
    parser.add_argument('fixture_files', metavar='N', type=str, nargs='+',
                        default='fixture_files', help='Fixure files to apply to the DB')
    return parser.parse_args()


def main():
    """The fixtures rollout entrypoint."""
    args = _parse_args()
    conf = BlueberryPyConfiguration(environment=args.environment)
    sqlalchemy_config = conf.sqlalchemy_config

    engine = engine_from_config(
        sqlalchemy_config['sqlalchemy_engine'],
        prefix='',
        poolclass=pool.NullPool
    )

    Session = sessionmaker(bind=engine)
    session = Session()

    for fixture_file in args.fixture_files:
        models = load_fixtures(fixture_file)
        session.add_all(models)

    session.commit()


if __name__ == '__main__':
    main()
