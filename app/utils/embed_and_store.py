from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma


def build_db():
    roles = ["engineering", "finance", "general", "hr", "marketing"]
    all_docs = []

    for role in roles:
        #print(role)
        #print(f"../../resources/data/{role}")
        loader = DirectoryLoader(f"../../resources/data/{role}", glob = "**/*.*")
        docs = loader.load()
        for doc in docs:
            doc.metadata["role"] = role
            doc.page_content = f"[ROLE: {role.upper()}]\n" + doc.page_content
            print(f"Added metadata to {len(docs)} docs for role: {role}")
            print(docs[0].metadata) 
        all_docs.extend(docs)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 300, chunk_overlap = 100)
    documents = text_splitter.split_documents(all_docs)

    db = Chroma.from_documents(documents[:], 
                               OllamaEmbeddings(), 
                               persist_directory="vectorstore",
                               collection_name="enterprise_docs")
    db.persist()

    return db

if __name__ == "__main__":
    db = build_db()
    print(db)




            
