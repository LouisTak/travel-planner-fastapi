from enum import Enum

class UserRole(Enum):
    """Enum for user roles in the system."""
    ADMIN = "admin"
    TESTER = "tester"
    PREMIUM = "premium"
    SUBSCRIBER = "subscriber"
    FREE = "free"
    
    @classmethod
    def has_value(cls, value):
        """Check if the enum has a specific value."""
        return value in [item.value for item in cls]
    
    @classmethod
    def get_default(cls):
        """Get the default role for new users."""
        return cls.FREE.value 