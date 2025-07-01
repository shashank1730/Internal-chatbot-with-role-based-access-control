# 🧠 VaultRAG Assistant: Secure Knowledge, Smarter Conversations

What if your company’s entire brain — finance reports, tech blueprints, HR handbooks — could chat with employees, give precise answers, and reveal just what each person needs to know?

**Welcome to VaultRAG Assistant** — an intelligent, secure, role-aware AI chatbot built for enterprise teams. It’s not just smart. It’s responsibly smart.

---

## 🔍 Why We Built It

Imagine a curious engineer poking around finance numbers, or a new hire trying to decode your company policies buried in files. Chaos, right?

We built this to fix that.

**Think of it like:**

- A digital librarian who whispers only the _right_ answers.
- A RAG-powered search engine that’s deeply aware of job roles.
- A security guard that says: “You shall not pass!” if someone tries to peek at unauthorized data.

---

## 🏗️ Architecture at a Glance

| Layer         | Tech Stack                                                   |
| ------------- | ------------------------------------------------------------ |
| **Backend**   | FastAPI + RAG                                                |
| **Frontend**  | Streamlit                                                    |
| **LLM**       | HuggingFace + Ollama                                         |
| **Vector DB** | ChromaDB                                                     |
| **Auth**      | Role-based (RBAC)                                            |
| **Storage**   | Markdown (.md) and CSV (.csv) chunked smartly with hierarchy |

---

## 📁 Folder Structure

```bash
.
├── app/                  # FastAPI backend
│   ├── main.py           # API endpoints
│   ├── services/         # RAG + CSV Agent logic
        ├──rag_engine.py
│   └── utils/
        ├──embed_and_store.py  # Embedding script
├── pages/
        ├──chat_bot.py                # Streamlit frontend
├── resources/data/       # Markdown & CSV files by role
├── requirements.txt
└── README.md
```

---

## 🔗 Key Components

- [🔐 RBAC Auth Logic](app/main.py)
- [📄 CSV Agent + LLM Verifier](app/services/rag_engine.py)
- [📚 VectorStore Embedding Script](app/utils/embed_and_store.py)
- [🧠 Frontend UI Logic](pages/chat_bot.py)

---

## 🧠 How We Handle Documents (This Is the Secret Sauce)

🧱 **Markdown + Metadata Magic**

We split documents not just randomly. Instead:

- First, we chunk using headers with hierarchy
- Then we keep those headings as metadata (like breadcrumbs).
- Finally, we use recursive chunking — slicing long parts while preserving their _contextual lineage_.

This way, every answer knows _where it came from_ — like a family tree for content.

📊 **CSV? No Problem**

- Parsed with `pandas`, transformed into Markdown tables.
- Tagged by department, then chunked like any other doc.

---

## 👤 Who Sees What? (RBAC That Makes Sense)

| Role             | Access                           |
| ---------------- | -------------------------------- |
| C-Level Exec     | 🔓 Everything                    |
| Engineering      | 🔧 Eng Docs + General Info       |
| Finance          | 💰 Finance Docs + General Info   |
| Marketing        | 📊 Marketing Docs + General Info |
| HR               | 👥 HR Docs + General Info        |
| General Employee | 📋 Just the Handbook             |

Every query response is filtered by role — no leaking, no oversharing.

---

## 🧩 Sample Interactions

- **C-Level**: “What’s our current tech stack?”
- **Engineer**: “Where’s the CI/CD flow defined?”
- **HR**: “What’s our leave utilization by department?”
- **Employee**: “How do I apply for maternity leave?”

And yes, it always shows you _where_ it pulled the answer from.

---

## 🛠️ How to Run It

````bash
# run the requirements.txt
pip install -r requirements.txt

```bash
# Storing the Vector DB (Run this once) -- Embeds all files into the vector store
python app/utils/embed_and_store.py

# Backend
uvicorn app.main:app --reload

# Frontend
streamlit run Streamlit_app.py
````

`.env` files are respected. HuggingFace keys and vector DB dirs are secure and never pushed.

---

## 🔐 Security Built-In

- 💼 Role-Based Access Control (RBAC)
- 🧾 Metadata tagging on every document chunk
- 🕵️‍♂️ Cross-role filtering in retrieval layer
- 🧱 Auth required for every endpoint (even chat)
- 🔐 Passwords never in plain text, API keys kept secret

---

## 🔮 Future Plans

- SSO Integration (LDAP/Google Auth)
- Document versioning and update detection
- Audit logs for compliance
- Query analytics dashboard
- Mobile-ready experience
- Multi-language support

---

## 🎥 Demo Preview

<p align="center">
  <img src="https://github.com/YOUR_USERNAME/YOUR_REPO/blob/main/demo.gif" width="700"/>
</p>

> Full walkthrough [📽️ on YouTube](https://youtu.be/your-video-link)

---

## 🏁 Final Words

VaultRAG Assistant isn’t just an internal chatbot. It’s:

- A smart gateway to your company knowledge
- A privacy-preserving, security-first solution
- A scalable foundation for every team’s AI-powered future

> _“Built with ♥ by a person who believes AI should empower, not expose.”_
