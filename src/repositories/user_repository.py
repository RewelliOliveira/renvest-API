from typing import Optional, Dict, Any
from src.core.database import get_supabase_client

class UserRepository:
    TABLE_NAME = "users"

    @classmethod
    def get_by_email(cls, email: str) -> Optional[Dict[str, Any]]:
        client = get_supabase_client()
        clean_email = email.strip().lower()
        response = client.table(cls.TABLE_NAME).select("*").ilike("email", clean_email).limit(1).execute()
        return response.data[0] if response.data else None

    @classmethod
    def get_by_id(cls, user_id: str) -> Optional[Dict[str, Any]]:
        client = get_supabase_client()
        response = client.table(cls.TABLE_NAME).select("*").eq("id", user_id).limit(1).execute()
        return response.data[0] if response.data else None

    @classmethod
    def get_by_google_id(cls, google_id: str) -> Optional[Dict[str, Any]]:
        client = get_supabase_client()
        response = client.table(cls.TABLE_NAME).select("*").eq("google_id", google_id).limit(1).execute()
        return response.data[0] if response.data else None

    @classmethod
    def create_local_user(cls, name: str, email: str, password_hash: str) -> Dict[str, Any]:
        client = get_supabase_client()
        clean_email = email.strip().lower()
        new_user_data = {
            "name": name.strip(),
            "email": clean_email,
            "password_hash": password_hash,
            "auth_provider": "local",
        }
        response = client.table(cls.TABLE_NAME).insert(new_user_data).execute()
        if not response.data:
            raise RuntimeError("Falha ao inserir usuário no banco de dados.")
        return response.data[0]

    @classmethod
    def upsert_google_user(
        cls,
        email: str,
        name: str,
        google_id: str,
        picture: Optional[str] = None
    ) -> Dict[str, Any]:
        client = get_supabase_client()
        clean_email = email.strip().lower()

        # Verifica se o usuário já existe por google_id
        existing_google = cls.get_by_google_id(google_id)
        if existing_google:
            update_data = {"name": name.strip()}
            if picture:
                update_data["picture"] = picture
            res = client.table(cls.TABLE_NAME).update(update_data).eq("id", existing_google["id"]).execute()
            return res.data[0] if res.data else existing_google

        # Se não existe por google_id, verifica se já existe uma conta local com o mesmo e-mail
        existing_email = cls.get_by_email(clean_email)
        if existing_email:
            update_data = {
                "google_id": google_id,
            }
            if picture and not existing_email.get("picture"):
                update_data["picture"] = picture
            res = client.table(cls.TABLE_NAME).update(update_data).eq("id", existing_email["id"]).execute()
            return res.data[0] if res.data else existing_email

        # Cria novo usuário via Google
        new_data = {
            "name": name.strip(),
            "email": clean_email,
            "google_id": google_id,
            "picture": picture,
            "auth_provider": "google",
        }
        response = client.table(cls.TABLE_NAME).insert(new_data).execute()
        if not response.data:
            raise RuntimeError("Falha ao criar usuário Google no banco de dados.")
        return response.data[0]
