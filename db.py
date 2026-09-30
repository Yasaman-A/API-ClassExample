import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")


def require_env(name):
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"Missing {name}. Add it to a .env file next to db.py "
            "(see env.example)."
        )
    return value


def get_db():
    return mysql.connector.connect(
        host=require_env("MYSQL_HOST"),
        port=int(os.environ.get("MYSQL_PORT", "3306")),
        user=require_env("MYSQL_USER"),
        password=require_env("MYSQL_PASSWORD"),
        database=require_env("MYSQL_DATABASE"),
    )

