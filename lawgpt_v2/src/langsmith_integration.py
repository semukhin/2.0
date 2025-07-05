import os

def enable_langsmith():
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "LawGPT-v2"
    # Можно добавить дополнительные настройки или интеграцию

if __name__ == "__main__":
    enable_langsmith()
    print("LangSmith tracing enabled.")
