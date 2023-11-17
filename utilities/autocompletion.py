class AutoComplete:
    '''Formats user input to match the format of the database'''

    def __init__(self, master):
        self.master = master

    def _insert_at_positions(self, entry, char, positions):
        '''Insert character at specific positions in the entry'''
        for pos in positions:
            if len(entry.get()) == pos:
                entry.insert(pos+1, char)

    def time_formatting(self, event, entry):
        '''Formats time input as hh:mm:ss'''
        self._insert_at_positions(entry, ':', [2, 5])

    def date_formatting(self, event, entry):
        '''Formats date input as yyyy-mm-dd'''
        self._insert_at_positions(entry, '-', [4, 7])

    def hs_formatting(self, event, entry):
        '''Formats hs input as dd-mm.t'''
        self._insert_at_positions(entry, '-', [2])
        self._insert_at_positions(entry, '.', [5])

    def lat_formatting(self, event, entry):
        '''Formats latitude input as dd-mm.t-N/S'''
        self._insert_at_positions(entry, '-', [2])
        self._insert_at_positions(entry, '.', [5])
        self._insert_at_positions(entry, '-', [7])
        # autocorrects lower cases
        lat_val = entry.get()
        if len(lat_val) == 9 and lat_val[-1] in ['n', 's']:
            entry.delete(8)
            entry.insert(9, lat_val[-1].upper())

    def long_formatting(self, event, entry):
        '''Formats longitude input as ddd-mm.t-E/W'''
        self._insert_at_positions(entry, '-', [3, 8])
        self._insert_at_positions(entry, '.', [6])
        # autocorrects lower cases
        long_val = entry.get()
        if len(long_val) == 10 and long_val[-1] in ['e', 'w']:
            entry.delete(9)
            entry.insert(10, long_val[-1].upper())
