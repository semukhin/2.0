import os
from dotenv import dotenv_values

REQUIRED_VARS = [
    "DATABASE_URL", "REDIS_URL", "SECRET_KEY", "ALGORITHM", "ACCESS_TOKEN_EXPIRE_MINUTES",
    "OPENAI_API_KEY", "TAVILY_API_KEY", "LANGCHAIN_API_KEY"
]

def main():
    env = dotenv_values(".env")
    missing = [var for var in REQUIRED_VARS if not env.get(var)]
    if missing:
        print(f"Missing variables: {', '.join(missing)}")
        exit(1)
    print("All required environment variables are set.")

if __name__ == "__main__":
    main()
