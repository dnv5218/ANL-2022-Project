from decimal import Decimal
from typing import TypeVar

from tudelft.utilities.immutablelist.ImmutableList import ImmutableList


E = TypeVar('E')
class ItemIterator:
    def __init__(self, l:ImmutableList[E]):
        self._l = l
        # member variable to keep track of current index
        self._index = 0
    def __next__(self):
        '''Returns the next value from team object's lists '''
        if self._index >= self._l.size():
            # End of Iteration
            raise StopIteration
        val=self._l.get(self._index)
        self._index += 1
        return val

class AbstractImmutableList(ImmutableList[E]):
    _PRINT_LIMIT = 20;
    
    def __iter__(self):
        return ItemIterator(self)
    
    def __repr__(self) :
        if self.size() > self._PRINT_LIMIT:
            end = self._PRINT_LIMIT;
        else:
            end = self.size()

        string = "[";
        for n in range(end):
            string += ( "," if n!=0 else "") + str(self.get(n))

        remain = self.size() - end
        if remain > 0:
            string += ",..." + str(remain) + " more..."

        string += "]";
        return string;

