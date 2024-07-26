import math

class HashGrid:
    def __init__(self, topY, rightX, bottomY, leftX, cell_size):
        self.topY = topY
        self.rightX = rightX
        self.bottomY = bottomY
        self.leftX = leftX
        self.cell_size = cell_size
        self.grid = {}
        self._init_grid()

    def _init_grid(self):
        xside = 1 + math.floor((self.rightX - self.leftX)/self.cell_size)
        yside = 1 + math.floor((self.topY - self.bottomY)/self.cell_size)
        for xi in range(xside):
            for yi in range(yside):
                x = self.leftX   + xi*self.cell_size
                y = self.bottomY + yi*self.cell_size
                self.grid[self.get_key(x, y)] = set()


    def get_index(self, value):
        return math.floor(value/ self.cell_size)

    def get_key(self, x, y):
        return self._get_key_by_indices(self.get_index(x), self.get_index(y))

    @staticmethod
    def _get_key_by_indices(xi, yi):
        return f"{xi}.{yi}"

    def add_item(self, item):
        key = self.get_key(item.x, item.y)
        if key not in self.grid:
            self.grid[key] = {item}
        else:
            self.grid[key].add(item)
        return self.grid[key]

    def remove_item(self, item):
        key = self.get_key(item.x, item.y)
        if key in self.grid:
            self.grid[key].discard(item)

    def query(self, x, y, radius):
        xi0 = self.get_index(x - radius) - 1
        xi1 = self.get_index(x + radius) + 1
        yi0 = self.get_index(y - radius) - 1
        yi1 = self.get_index(y + radius) + 1
        result = set()
        for xi in range(xi0, xi1 + 1):
            for yi in range(yi0, yi1 + 1):
                key = self._get_key_by_indices(xi, yi)
                if key in self.grid:
                    result.update(self.grid[key])
        return result

    def create_client(self, item):
        return HashGridClient(self, item)


class HashGridClient:
    def __init__(self, hash_grid, item):
        self.hash_grid = hash_grid
        self.item = item
        self.indexX = self.hash_grid.get_index(item.x)
        self.indexY = self.hash_grid.get_index(item.y)
        self.cell = self.hash_grid.add_item(item)

    def update(self):
        newIndexX = self.hash_grid.get_index(self.item.x)
        newIndexY = self.hash_grid.get_index(self.item.y)
        if newIndexX == self.indexX and newIndexY == self.indexY:
            return

        self.cell.discard(self.item)
        self.cell = self.hash_grid.add_item(self.item)
        self.indexX = newIndexX
        self.indexY = newIndexY

    def delete(self):
        self.cell.discard(self.item)

