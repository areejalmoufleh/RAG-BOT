# تخزين مؤقت في الذاكرة (يعمل 100% بدون Redis)
memory_store = {}

def get_history(session_id: str):
    return memory_store.get(session_id, [])

def save_history(session_id: str, history: list):
    memory_store[session_id] = history[-20:]

def add_message(session_id: str, role: str, content: str):
    history = get_history(session_id)
    history.append({"role": role, "content": content})
    save_history(session_id, history)
    return history