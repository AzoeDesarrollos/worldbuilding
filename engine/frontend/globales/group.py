class Group:
    """A disclosed imitation of Pygame's Layered Updates Group

    It can take strings as layers as well as ints.
    """

    def __init__(self):
        self._d = {}
        self._list = []
        self._leght = 0

    def add(self, *item, layer=1):
        if layer not in self._d:
            self._d[layer] = []

        for unit in item:
            self._d[layer].append(unit)
            self._list.append(unit)
            self._leght += 1

    def remove(self, item):
        layer = None
        for layer in self._d:
            if item in self._d[layer]:
                break
        self._d[layer].remove(item)
        if not len(self._d[layer]):
            del self._d[layer]
        self._list.remove(item)
        self._leght -= 1

    def clear_layer(self, layer):
        for item in self._d[layer]:
            self._list.remove(item)
            self._leght -= 1
        del self._d[layer]

    def get_widgets_from_layer(self, layer):
        if layer in self._d:
            return self._d[layer]
        else:
            return []

    def change_layer(self, sprite, layer):
        self.remove(sprite)
        self.add(sprite, layer=layer)

    def widgets(self):
        return self._list

    def get_widget(self, id):
        for item in self._list:
            if hasattr(item, 'id') and item.id == id:
                return item

        if type(id) is int and 0 <= id <= len(self._list):
            return self._list[id]

    def __len__(self):
        return self._leght

    def empty(self):
        self._d.clear()
        self._list.clear()
        self._leght = 0

    def __repr__(self):
        return str(self._list)

    def __contains__(self, item):
        if hasattr(item, 'name'):
            candidates = [i for i in self._list if i.name == item.name]
            if len(candidates):
                return True
            return False
        else:
            return item in self._list

    def draw(self, bg):
        for each in self._list:
            bg.blit(each.image, each.rect)

    def update(self):
        for each in self._list:
            each.update()
