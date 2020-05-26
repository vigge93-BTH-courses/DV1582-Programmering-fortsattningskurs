class Library:
    """Library class."""

    def __init__(self):
        """Initialize library."""
        self._available = {}
        self._loaned = {}

    def to_dict(self):
        """Convert the book library to a dictionary."""
        return {
            'available': [book.to_dict for book in self._available],
            'loaned': [book.to_dict for book in self._loaned],
        }

    @classmethod
    def from_dict(cls, dict_):
        """Restore the book library from a dictionary."""
        library = cls()
        library._available = [Book.from_dict(book) for book in dict_['available']]
        library._loaned = [Book.from_dict(book) for book in dict_['loaned']]
        return library


class Book:
    """Book class."""

    def __init__(self, title, author, isbn):
        """Initialize book."""
        self._title = title
        self._author = author
        self._isbn = isbn

    def to_dict(self):
        """Convert book to a dictionary."""
        return {
            'title': self._title,
            'author': self._author,
            'isbn': self._isbn,
        }

    @classmethod
    def from_dict(cls, dict_):
        """Restore book from a dictionary."""
        return cls(dict_['title'], dict_['author'], dict_['isbn'])
