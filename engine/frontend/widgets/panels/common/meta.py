
class Meta:
    enabled = False
    img_sel = None
    img_uns = None
    img_dis = None
    selected = False
    image = None

    is_visible = False
    has_mouseover = False

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False
        self.image = self.img_dis

    def on_mouseover(self):
        self.has_mouseover = True
        if self.enabled:
            self.image = self.img_sel

    def select(self):
        self.selected = True
        if self.enabled:
            self.image = self.img_sel

    def deselect(self):
        self.selected = False
        self.image = self.img_uns

    def update(self):
        if all([not self.has_mouseover, not self.selected, self.enabled]):
            self.image = self.img_uns
        self.has_mouseover = False
