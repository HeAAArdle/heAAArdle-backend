import uuid

def generate_token() -> str:
    """
    Generates a unique authentication token.
    """
    return str(uuid.uuid4())
