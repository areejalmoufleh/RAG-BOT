import os
import glob
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document

load_dotenv()

CHROMA_PATH = "data/chroma_db"
RAW_DIR = "data/raw"

# نموذج التضمين المحلي (نفس الذي نجح في مشروعك السابق)
embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
documents = []

for filepath in glob.glob(os.path.join(RAW_DIR, "*.txt")):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    source = os.path.basename(filepath).replace(".txt", "").replace("_", "/")
    chunks = text_splitter.split_text(text)
    for chunk in chunks:
        documents.append(Document(page_content=chunk, metadata={"source": source}))

# Chroma ستُنشئ قاعدة وتحفظها تلقائياً في CHROMA_PATH
vectordb = Chroma.from_documents(
    documents=documents,
    embedding=embedding,
    persist_directory=CHROMA_PATH
)
vectordb.persist()
print(f"✅ تم فهرسة {len(documents)} مقطعاً في Chroma.")