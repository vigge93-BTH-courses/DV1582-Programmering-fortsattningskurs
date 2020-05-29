class Media:
    """Base class for media."""

    def __init__(self, title, author, isbn):
        """Initialize media."""
        self._author = author
        self._title = title
        self._isbn = isbn
        self._queue = Queue()

    def add_to_waitlist(self, customer):
        """Add a customer to the waitlist."""
        self._queue.enqueue(customer)

    def get_from_waitlist(self):
        """Remove and return a customer from the waitlist."""
        return self._queue.dequeue()

    def to_dict(self):
        """Create a dictionary from the media object."""
        d = {
            'title': self._title,
            'author': self._author,
            'isbn': self._isbn,
            'queue': []
        }

        # Preserve the queue
        temp_queue = Queue()
        while len(self._queue) > 0:
            customer = self._queue.dequeue()
            d['queue'].append(customer.to_dict())
            temp_queue.enqueue(customer)
        self._queue = temp_queue

        return d


class Book(Media):
    """Book class, inherits from Media."""

    def __init__(self, title, author, isbn, pages):
        """Initialize book."""
        super().__init(title, author, isbn)
        self._pages = pages

    def to_dict(self):
        """Create a dictionary from the book object."""
        d = super().to_dict()
        d['pages'] = self._pages
        return d


class AudioBook(Media):
    """Auidobook class, inherits from Media."""

    def __init__(self, title, author, isbn, url):
        """Initialize audiobook."""
        super().__init__(title, author, isbn)
        self._url = url

    def to_dict(self):
        """Create a dictionary from the audiobook object."""
        d = super().to_dict()
        d['url'] = self._url
        return d
