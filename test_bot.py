from app.rag_pipeline import get_answer

session_id = "test"
print("🤖 بوت المعرفة (Chroma + Gemini) - اكتب exit للخروج")
while True:
    q = input("\nسؤالك: ")
    if q.lower() == "exit":
        break
    ans, srcs = get_answer(q, session_id)
    print(f"الإجابة: {ans}")
    print(f"المصادر: {srcs}")