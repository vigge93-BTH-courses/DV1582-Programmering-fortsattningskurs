from threading import Thread


class Book:
    """Book class."""

    def __init__(self, isbn):
        """Initialize book"""
        self._queue = Queue()
        self._isbn = isbn

    @property
    def isbn(self):
        """Return ISBN of book"""
        return self._isbn

    def get_from_waitlist(self):
        """Get the next person from the waitlist."""
        if len(self._queue) > 0:
            return self._queue.dequeue()
        else:
            return None


class Customer:
    """Customer class."""
    def __init__(self, library):
        """Initialize customer."""
        self._books = {}
        self._library = library

    def return_book(self, isbn):
        """Return the book."""
        return_thread = ReturnThread(self._books[isbn], self._library)
        return_thread.start()

    def give_book(self, book):
        """Give a book to the customer."""
        self._books[book.isbn] = book

    def want_book(self, isbn):
        """Check if customer wants the book"""
        pass

    class ReturnThread(Thread):
        """Class for returning the book"""
        def __init__(self, book, library):
            """Initialize book return class"""
            self._book = book
            self._library = library

        def run(self):
            """Return the book."""
            self._library.return_book(self._book)


class Library:
    """Library class."""

    def __init__(self):
        """Initialize library."""
        self._available_books = {}
        self._loaned_books = {}

    def return_book(self, book):
        """Return a book and loan it to somoeone on the waitlist if applicable."""
        while (next_customer := book.get_from_waitlist()):
            if next_customer.want_book():
                next_customer.give_book(book)
                return
        self._available_books[book.isbn] = book
        del self._loaned_books[book.isbn]

