from abc import ABC, abstractmethod
import io, typing
from typing import Tuple, Mapping, Callable

#FileNotFoundError
#io.BlockingIOError
#io.UnsupportedOperation

class DjlfsBatchStorageBase(ABC):

    @abstractmethod
    def get_size(self, oid:str) -> int:
        '''Get OID file size in bytes (or raise a FileNotFoundError if it doesn't exist)'''
        raise io.UnsupportedOperation

    @abstractmethod
    def open_as_url(self, oid:str, mode:str) -> Tuple[ str, Mapping[str, str] ]:
        '''
        Get a tuple of...
          1) direct URL for reading (mode 'r') or writing (mode 'w') an object, and
          2) a dict of headers necessary for the request.
        ...or None if direct URL access is not supported.
        '''
        return None

    @abstractmethod
    def open_as_file(self, oid:str, mode:str) -> Tuple[ io.RawIOBase, Callable, Callable ]:
        '''
        Open object with given oid for reading (mode 'r') or writing (mode 'w'), and
        Return a tuple of...
          1) File-like object to read / write
          2) Function to call when write succeeded (read may not call this, override close() if necessary)
          3) Function to call when write failed  (read may not call this)
        ...or None if file-like access is not supported.
        '''
        return None
