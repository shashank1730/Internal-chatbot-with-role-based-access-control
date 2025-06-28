from langchain.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_ollama import OllamaLLM
import streamlit as st
from langchain.chains import create_retrieval_chain
from langchain_community.embeddings import OllamaEmbeddings
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import os

def get_rag_response(query: str, role:str) -> str:
    #role = "marketing"
    llm = OllamaLLM(model="llama3.2", temperature=0)

    prompt = ChatPromptTemplate.from_template("""
       You are an expert assistant with access to internal company documents. Your only source of truth is the content provided in <context>.

        Each chunk begins with heading labels: `h1:`, `h2:`, `h3:`, and `h4:` — these are actual section titles from the document. Use them to understand what topic the content belongs to.

        <context>
        {context}
        </context>

        User Question: {input}

        Instructions:
        - Use the section titles (h1–h4) to guide your understanding of each chunk’s context.
        - Answer clearly and concisely, as if briefing an executive.
        - If the content under a heading suggests relevance but no exact answer is provided, you may cautiously infer.
        - If the answer is not explicitly or reasonably inferable, reply: "The provided documents do not contain this information."
    """)



    document_chain = create_stuff_documents_chain(llm, prompt)

    db = Chroma(
        persist_directory="resources/vectorstore",
        embedding_function = HuggingFaceEmbeddings(
                model_name="nomic-ai/nomic-embed-text-v1",
                model_kwargs={"trust_remote_code": True},
                cache_folder="./models"
            ),
    )

    print("Reloaded docs:", db._collection.get()['metadatas'][:5])

    if role == "C-Level Executives":
        retriever = db.as_retriever(search_kwargs={"k":6})
    else:
        retriever = db.as_retriever(search_kwargs={"filter":{"role":role}, "k":6})


    docs = retriever.get_relevant_documents(query)
    print(f"🔎 Retrieved {len(docs)} documents for role: {role}")
    for d in docs:
        print(f"📄 {d.metadata.get('source')} | Role: {d.metadata.get('role')}")

    
    sources = []
    for doc in docs:
        source_path = doc.metadata.get("source")
        if source_path:
            file_name = os.path.basename(source_path)
            link = f"http://localhost:8000/files/{'/'.join(source_path.split(os.sep)[-2:])}"
        else:
            file_name = "Unknown"
            link = "#"

        sources.append({
            "file_name": file_name,
            "link": link
        })
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    inputs = {"input": query, "role": role}
    response = retrieval_chain.invoke(inputs)


    print("\n💬 Final Answer:\n", response['answer'])

    answer = response["answer"]
    return answer, sources

    


    #print(response['answer'])


