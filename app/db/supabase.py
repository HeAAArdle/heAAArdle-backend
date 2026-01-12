from app.core.config import settings

from supabase import create_client, Client

assert settings.supabase_url is not None, "Missing Supabase URL in .env."
assert settings.supabase_key is not None, "Missing Supabase key in .env."

supabase: Client = create_client(settings.supabase_url, settings.supabase_key)
