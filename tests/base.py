from datetime import datetime

class Base(object):
    """Base class for test classes."""

    @property
    def timestamp(self):
        return datetime.utcnow().isoformat()
