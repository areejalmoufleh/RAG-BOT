import os
from typing import List, Tuple
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from .session import get_history, add_message

load_dotenv()

CHROMA_PATH = "data/chroma_db"

embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

def get_answer(user_message: str, session_id: str) -> Tuple[str, List[str]]:
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    vectordb = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding)
    retriever = vectordb.as_retriever(search_kwargs={"k": 5})

    # إعداد الذاكرة من Redis
    history = get_history(session_id)
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        output_key="answer",
        return_messages=True
    )
    for msg in history:
        if msg["role"] == "user":
            memory.chat_memory.add_user_message(msg["content"])
        else:
            memory.chat_memory.add_ai_message(msg["content"])

    qa = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        output_key="answer",
        return_source_documents=True,
    )
    result = qa.invoke({"question": user_message})
    answer = result["answer"]
    sources = list(set([doc.metadata.get("source", "unknown") for doc in result.get("source_documents", [])]))

    # تحديث Redis بآخر رسالتين فقط
    add_message(session_id, "user", user_message)
    add_message(session_id, "assistant", answer)

    return answer, sources