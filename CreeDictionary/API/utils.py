from sortedcontainers import SortedSet


class SortedSetWithExtend(SortedSet):
    def extend(self, items):
        for it in items:
            self.add(it)
