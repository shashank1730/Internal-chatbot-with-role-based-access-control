from langchain.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_ollama import OllamaLLM
import streamlit as st
from langchain.chains import create_retrieval_chain
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma


role = "finance"
llm = OllamaLLM(model="llama2")

prompt = ChatPromptTemplate.from_template(""" 
You are an intelligent, secure document assistant for an enterprise knowledge system.

Your responsibilities:
1. Search through **only the documents the user is authorized to access** (based on their role).
2. Provide **concise, relevant, context-rich answers** based only on the retrieved content.
3. If the answer comes from a document, always **include the document title and a clickable link** to the source.
4. If the user's question is **outside their access scope**, politely inform them they do not have access and do **not attempt to answer** using external or unauthorized data.

---

Context Available to You:
{context}

User Role: {role}

User Question:
{input}

---

Instructions:
- You MUST ONLY use the provided context to generate your response.
- If the context does not contain enough information to answer the question, you MUST reply:
  "You currently do not have access to the documents required to answer this question."
- You are NOT ALLOWED to use your own knowledge or any external data.
- If a document is used, provide the response along with:  
  `Document: [Document Title](Document Link)`



""")


document_chain = create_stuff_documents_chain(llm, prompt)

db = Chroma(
    persist_directory="app/utils/vectorstore",
    embedding_function=OllamaEmbeddings(),
    collection_name="enterprise_docs"
)

#print("Reloaded docs:", db._collection.get()['metadatas'][:5])


retriever = db.as_retriever(search_kwargs={"filter":{"role":role}})

docs = retriever.get_relevant_documents("give summary on financial metrics of this company")
print(f"🔎 Retrieved {len(docs)} documents for role: {role}")
for d in docs:
    print(f"📄 {d.metadata.get('source')} | Role: {d.metadata.get('role')}")


retrieval_chain = create_retrieval_chain(retriever, document_chain)

inputs = {"input": "give summary on financial metrics of this company", "role": "finance"}
response = retrieval_chain.invoke(inputs)

print("\n💬 Final Answer:\n", response['answer'])

# Extract and show context if possible
if hasattr(response, 'intermediate_steps'):
    print("📚 Context from intermediate steps:", response.intermediate_steps)


#print(response['answer'])


