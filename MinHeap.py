class MinHeap:
    def __init__(self):
        self.heap = []
        self.position = {}

    def swap_nodes(self, i, j):
        self.position[self.heap[i][0]] = j
        self.position[self.heap[j][0]] = i
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def heapify_down(self, index):
        left = 2 * index + 1
        right = 2 * index + 2
        smallest = index

        if(left < len(self.heap) and self.heap[left][1] < self.heap[smallest][1]):
            smallest = left
        if(right < len(self.heap) and self.heap[right][1] < self.heap[smallest][1]):
            smallest = right

        if smallest != index:
            self.swap_nodes(index, smallest)
            self.heapify_down(smallest)

    def heapify_up(self, index):
        parent = (index - 1) // 2
        if (index > 0 and self.heap[index][1] < self.heap[parent][1]):
            self.swap_nodes(index, parent)
            self.heapify_up(parent)

    def insert(self, vertex, dist):
        self.heap.append((vertex, dist))
        index = len(self.heap) - 1
        self.position[vertex] = index
        self.heapify_up(index)

    def extract_min(self):
        vertex, dist = self.heap[0]
        self.swap_nodes(0, len(self.heap) - 1)
        self.position.pop(vertex)
        self.heap.pop()
        if self.heap:
            self.heapify_down(0)
        return vertex, dist

    def decrease_key(self, vertex, newDist):
        index = self.position[vertex]
        self.heap[index] = (vertex, newDist)
        self.heapify_up(index)

    def contains(self, vertex):
        return vertex in self.position

    def empty(self):
        return not self.heap

