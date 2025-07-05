import os
from pathlib import Path
from dotenv import dotenv_values

REQUIRED_VARS = [
    "DATABASE_URL", "REDIS_URL", "SECRET_KEY", "ALGORITHM", "ACCESS_TOKEN_EXPIRE_MINUTES",
    "OPENAI_API_KEY", "TAVILY_API_KEY", "LANGCHAIN_API_KEY"
]

def main():
    env_path = Path(".env")
    if env_path.exists():
        print(".env already exists.")
        return
    with open(env_path, "w", encoding="utf-8") as f:
        for var in REQUIRED_VARS:
            f.write(f"{var}=\n")
    print(".env file generated with required variables.")

if __name__ == "__main__":
    main()
