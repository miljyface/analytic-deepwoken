VERSION = '1.0.0'
AUTHOR = 'Pom'
DESCRIPTION = 'Handler methods for the Python-based analytics bot for the Deepwoken Institute of Building (DWIB)'
license = 'MIT'

from .commandManager import commandManager
from .backbone import fetch_table, searchTableByName, searchTableById
from .spellCheck import find

__all__ = [
    'commandManager',
    'fetch_table',
    'searchTableByName',
    'searchTableById',
    'find'
]