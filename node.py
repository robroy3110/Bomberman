class Node:

    parent = None
    weight = None
    direction = 1

    def __init__(self, px, py, reach, base_weight, value):
        self.x = px
        self.y = py
        self.reach = reach
        self.base_weight = base_weight
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)
