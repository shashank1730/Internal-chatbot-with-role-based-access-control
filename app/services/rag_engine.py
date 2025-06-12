from langchain.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_ollama import OllamaLLM
import streamlit as st
from langchain.chains import create_retrieval_chain
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

def get_rag_response(query: str, role:str) -> str:
    #role = "marketing"
    llm = OllamaLLM(model="llama2")

    prompt = ChatPromptTemplate.from_template(""" 
    You are an intelligent, secure document assistant for an enterprise knowledge system.

    Your responsibilities:
    1. You MUST search only through all the available documents.
    2. You MUST provide concise, relevant answers using ONLY the retrieved content.
    3. You MUST NOT answer if the question is outside the context or access level.


    ---

    Context Available to You:
    {context}

    User Role: {role}

    User Question:
    {input}

    ---

    Instructions:

    - DO provide any partial summaries, guesses, or additional commentary.
    - DO NOT generate any content from memory or general knowledge.
    - DO NOT attempt to rephrase or explain why the answer isn't possible — just use the exact line above.




    """)


    document_chain = create_stuff_documents_chain(llm, prompt)

    db = Chroma(
        persist_directory="app/utils/vectorstore",
        embedding_function=OllamaEmbeddings(),
        collection_name="enterprise_docs"
    )

    print("Reloaded docs:", db._collection.get()['metadatas'][:5])


    retriever = db.as_retriever(search_kwargs={"filter":{"role":role}})

    docs = retriever.get_relevant_documents(query)
    print(f"🔎 Retrieved {len(docs)} documents for role: {role}")
    for d in docs:
        print(f"📄 {d.metadata.get('source')} | Role: {d.metadata.get('role')}")


    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    inputs = {"input": query, "role": role}
    response = retrieval_chain.invoke(inputs)


    print("\n💬 Final Answer:\n", response['answer'])

    return response['answer']

    


    #print(response['answer'])


