from supabase.client import supabase

def signup(email: str, password: str):
    return supabase.auth.sign_up({"email": email, "password": password})

def login(email: str, password: str):
    return supabase.auth.sign_in_with_password({"email": email, "password": password})
