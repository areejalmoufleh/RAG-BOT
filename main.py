from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from app.rag_pipeline import get_answer

app = FastAPI()

class ChatRequest(BaseModel):
    message: str
    session_id: str

@app.get("/", response_class=HTMLResponse)
async def home():
    html = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>بوت المعرفة</title>
        <style>
            :root {
                --primary: #6C5CE7;
                --surface: #1A1A2E;
                --bg: #0F0F1A;
                --text: #FFFFFF;
            }
            * { margin:0; padding:0; box-sizing:border-box; }
            body {
                background: var(--bg);
                color: var(--text);
                font-family: 'Segoe UI', sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .container {
                width: 800px;
                max-width: 95%;
                background: var(--surface);
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.5);
                display: flex;
                flex-direction: column;
                height: 90vh;
            }
            .header {
                padding: 15px 20px;
                background: #252542;
                border-radius: 20px 20px 0 0;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .chat-box {
                flex:1;
                overflow-y: auto;
                padding: 16px;
                display: flex;
                flex-direction: column;
                gap: 12px;
            }
            .msg {
                max-width: 80%;
                padding: 10px 14px;
                border-radius: 16px;
                line-height: 1.5;
                word-wrap: break-word;
            }
            .msg.user {
                align-self: flex-end;
                background: var(--primary);
                border-bottom-right-radius: 4px;
            }
            .msg.bot {
                align-self: flex-start;
                background: #252542;
                border-bottom-left-radius: 4px;
            }
            .sources {
                font-size: 12px;
                color: #B0B0C0;
                margin-top: 5px;
                border-top: 1px solid rgba(255,255,255,0.1);
                padding-top: 5px;
            }
            .input-area {
                display: flex;
                padding: 10px;
                background: #252542;
                border-radius: 0 0 20px 20px;
            }
            .input-area input {
                flex: 1;
                padding: 10px;
                background: #1A1A2E;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 10px;
                color: white;
            }
            .input-area button {
                margin-right: 8px;
                padding: 10px 20px;
                background: var(--primary);
                border: none;
                color: white;
                border-radius: 10px;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <span>🤖</span>
                <h3>بوت المعرفة</h3>
            </div>
            <div class="chat-box" id="chat"></div>
            <div class="input-area">
                <input type="text" id="userInput" placeholder="اسأل هنا...">
                <button onclick="sendMsg()">إرسال</button>
            </div>
        </div>

        <script>
            const chat = document.getElementById('chat');
            const sessionId = 'web_' + Date.now();

            function addMsg(role, text, sources) {
                const div = document.createElement('div');
                div.className = 'msg ' + role;
                div.textContent = text;
                chat.appendChild(div);
                if (sources && sources.length) {
                    const srcDiv = document.createElement('div');
                    srcDiv.className = 'sources';
                    srcDiv.textContent = '📚 ' + sources.join('، ');
                    chat.appendChild(srcDiv);
                }
                chat.scrollTop = chat.scrollHeight;
            }

            async function sendMsg() {
                const input = document.getElementById('userInput');
                const msg = input.value.trim();
                if (!msg) return;
                addMsg('user', msg);
                input.value = '';
                try {
                    const res = await fetch('/chat', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({message: msg, session_id: sessionId})
                    });
                    const data = await res.json();
                    addMsg('bot', data.answer, data.sources);
                } catch(e) {
                    addMsg('bot', '❌ خطأ في الاتصال');
                }
            }

            document.getElementById('userInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') sendMsg();
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        answer, sources = get_answer(request.message, request.session_id)
        return {"answer": answer, "sources": sources}
    except Exception as e:
        return {"answer": f"خطأ: {str(e)}", "sources": []}