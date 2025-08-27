# app/supabase_client.py
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise RuntimeError("Les variables SUPABASE_URL ou SUPABASE_KEY sont manquantes.")

supabase: Client = create_client(url, key)
