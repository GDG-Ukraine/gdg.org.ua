#!/usr/bin/env python3

import importlib
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import yaml


def import_class(what):
    """ Imports a class by given full name
    Args:
        what (str): a string with full classname to import
    Return:
        (type): a class which has been imported
    """
    modulename, classname = what.rsplit('.', 1)
    module = importlib.import_module(modulename)
    return getattr(module, classname)


def load_fixtures(filepath):
    """ Loads fixtures from given file
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


def main():
    db_url, *filepathes = sys.argv[1:]

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    for filepath in filepathes:
        models = load_fixtures(filepath)
        session.add_all(models)

    session.commit()


if __name__ == '__main__':
    main()
