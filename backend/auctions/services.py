import secrets

def generate_invite_code():
    return secrets.token_urlsafe(16)

