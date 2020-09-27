from engine import open_float_list_txt
from .star import Star


class Galaxy:
    name = ''

    def __init__(self):
        data = open_float_list_txt('data/main_sequences.txt')
        self._groups = {name: StarGroup(name) for name in 'OBAFGKM'}

        for mass in data:
            self.append(Star({'mass': mass}))

    def __getitem__(self, item):
        # item could be a group (only it's letter)
        # or a specific star (in that case, item would be
        # the star's name or code). In any case, it's a str
        if len(item) == 1:  # a star group key
            return self._groups[item]
        elif '#' in item:  # the star's code:
            return self._groups[item[0]][item]  # the star group key
        else:
            # there's no way to get star's fantasy name, yet.
            raise NotImplemented()

    def append(self, value):
        # this is a shortcut to add stars to their
        # respective groups. Adding stars directly to the
        # galaxy makes no sense. Adding Black Holes on the
        # other hand...
        key = value.cls  # value is a star, so it has a cls
        self._groups[key].append(value)

    def __delitem__(self, key):
        # when stars go supernova :P
        pass

    def __contains__(self, item):
        # same as __getitem__()
        return self.__getitem__(item) is not None

    def __len__(self):
        values = list(self._groups.values())
        return sum([int(i) for i in values])

    def __repr__(self):
        return 'Galaxy {} ({} stars)'.format(self.name, len(self))


class StarGroup:

    def __init__(self, class_name):
        self.name = class_name  # G
        self._group = {}
        self._indexes = []

    @property
    def _lenght(self):
        return len(self._indexes)

    def __getitem__(self, item):
        if type(item) is int:  # the star's index within the group
            if 0 <= item <= len(self._indexes) - 1:
                return self._group[self._indexes[item]]
            else:
                raise IndexError

        elif type(item) is str:  # the star's name
            if item in self._group:
                return self._group[item]

        else:
            raise KeyError

    def append(self, value):
        numkey = value.cls + '#' + str(self._lenght)
        if numkey not in self._group:
            self._group[numkey] = value  # key should be the star's name; its ID
            self._indexes.append(value)

    def __delitem__(self, key):
        if key in self._group:
            self._indexes.remove(key)
            del self._group[key]

        elif type(key) is int:
            if 0 <= key <= len(self._indexes) - 1:
                del self._group[self._indexes[key]]
                del self._indexes[key]
            else:
                raise IndexError
        else:
            raise KeyError

    def __contains__(self, item):
        if type(item) is str:
            if item in self._group:
                return True

        elif type(item) is int:
            if 0 <= item <= len(self._indexes) - 1:
                if self._indexes[item] in self._group:
                    return True
                else:
                    raise IndexError

        return False

    def __len__(self):
        return self._lenght

    def __int__(self):
        return self._lenght

    def __repr__(self):
        return 'StarGroup "{}" ({} stars)'.format(self.name, str(self._lenght))
