"""
ATUM DESK - Password Policy Validator
"""
import re

# Common weak passwords (top 100)
COMMON_PASSWORDS = {
    "password", "123456", "12345678", "qwerty", "abc123", "monkey", "1234567",
    "letmein", "trustno1", "dragon", "baseball", "iloveyou", "master", "sunshine",
    "ashley", "bailey", "shadow", "123123", "654321", "superman", "qazwsx",
    "michael", "football", "password1", "password123", "welcome", "welcome1",
    "admin", "login", "starwars", "1234567890", "passw0rd", "hello", "charlie",
    "donald", "princess", "qwerty123", "666666", "7777777", "121212", "flower",
    "hottie", "loveme", "zaq1zaq1", "password2", "555555", "888888", "fuckoff",
    "fuckyou", "hacker", "jordan", "jennifer", "zxcvbnm", "asdfgh", "hunter",
    "buster", "soccer", "harley", "batman", "andrew", "tigger", "sunflower",
    "数码", "password12", "hello123", "google", "youtube", "amazon", "facebook",
    "instagram", "twitter", "linkedin", "github", "gitlab", "bitbucket", "jira",
    "confluence", "slack", "discord", "teams", "zoom", "meet", "dropbox", "onedrive",
    "123456789", "0987654321", "password!", "P@ssw0rd", "P@ssword1", "Summer2024",
    "Winter2024", "Spring2024", "Autumn2024", "January", "February", "March", "April"
}

MIN_LENGTH = 12
MAX_LENGTH = 128


def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password against policy.
    Returns (is_valid, error_message)
    """
    if len(password) < MIN_LENGTH:
        return False, f"Password must be at least {MIN_LENGTH} characters long"
    
    if len(password) > MAX_LENGTH:
        return False, f"Password must not exceed {MAX_LENGTH} characters"
    
    if password.lower() in COMMON_PASSWORDS:
        return False, "Password is too common. Choose a stronger password"
    
    # Check character requirements
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>/?\\|`~]', password))
    
    if not (has_upper and has_lower and has_digit and has_special):
        return False, "Password must include uppercase, lowercase, number, and special character"
    
    return True, ""


def get_password_requirements() -> dict:
    """Return password requirements for UI"""
    return {
        "min_length": MIN_LENGTH,
        "max_length": MAX_LENGTH,
        "require_uppercase": True,
        "require_lowercase": True,
        "require_digit": True,
        "require_special": True,
        "block_common": True
    }
