class Queue:
    """Queue class."""

    def __init__(self):
        """Initialize queue."""
        self._queue = []

    def enqueue(self, el):
        """Add an element to the queue."""
        self._queue.append(el)

    def deque(self):
        """Get and remove the first element in the queue."""
        if len(self._queue) == 0:
            raise ValueError
        return self._queue.pop(0)

    def size(self):
        """Return the current size of the queue."""
        return len(self._queue)

    def __len__(self):
        """Return the current size of the queue."""
        return len(self._queue)

    def peek(self):
        """Peek at the first element in the queue."""
        return self._queue[0]
