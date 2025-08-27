from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Les variables SUPABASE_URL ou SUPABASE_KEY sont manquantes.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
