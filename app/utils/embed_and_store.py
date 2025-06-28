from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
import pandas as pd
import os
from langchain.embeddings import HuggingFaceEmbeddings



def build_db():
    roles = ["engineering", "hr", "marketing", "finance", "general"]
    all_final_chunks = []

    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[
        ("#", "h1"),
        ("##", "h2"),
        ("###", "h3"),
        ("####", "h4")
    ])
    recursive_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    for role in roles:
        role_path = f"resources/data/{role}"

        # --- Process Markdown files ---
        md_loader = DirectoryLoader(
            role_path,
            glob="**/*.md",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"}
        )
        md_docs = md_loader.load()

        md_chunks = []
        for doc in md_docs:
            doc.metadata["role"] = role
            chunks = markdown_splitter.split_text(doc.page_content)
            for chunk in chunks:
                chunk.metadata |= doc.metadata
            md_chunks.extend(chunks)

        # Further chunk markdown content recursively
        md_chunks = recursive_splitter.split_documents(md_chunks)

        # Re-attach hierarchical headers to each chunk
# Re-attach structured heading labels (h1, h2, ...) to chunk content
        final_md_chunks = []
        for chunk in md_chunks:
            header_lines = []
            if chunk.metadata.get("h1"):
                header_lines.append(f"h1: {chunk.metadata['h1']}")
            if chunk.metadata.get("h2"):
                header_lines.append(f"h2: {chunk.metadata['h2']}")
            if chunk.metadata.get("h3"):
                header_lines.append(f"h3: {chunk.metadata['h3']}")
            if chunk.metadata.get("h4"):
                header_lines.append(f"h4: {chunk.metadata['h4']}")
            
            headers = "\n".join(header_lines).strip()
            content = f"{headers}\n\n{chunk.page_content}" if headers else chunk.page_content
            final_md_chunks.append(Document(page_content=content, metadata=chunk.metadata))


        all_final_chunks.extend(final_md_chunks)

        # --- Process CSV files ---
        '''for filename in os.listdir(role_path):
            if filename.endswith(".csv"):
                filepath = os.path.join(role_path, filename)
                try:
                    df = pd.read_csv(filepath)
                    markdown_table = df.to_markdown(index=False)
                    doc = Document(
                        page_content=f"[ROLE: {role.upper()}] - CSV File: {filename}\n\n{markdown_table}",
                        metadata={"role": role, "source": filepath, "type": "csv"}
                    )
                    all_final_chunks.append(doc)
                except Exception as e:
                    print(f"❌ Error loading {filename}: {e}")'''
    print(all_final_chunks)
    print(f"\n✅ Final document count: {len(all_final_chunks)}")

    db = Chroma.from_documents(
        all_final_chunks,
        HuggingFaceEmbeddings(
            model_name="nomic-ai/nomic-embed-text-v1",
            model_kwargs={"trust_remote_code": True},
            cache_folder="./models"
        ),
        persist_directory="resources/vectorstore"
    )
    db.persist()
    print("\n🎉 Embedding and storage complete!")

    return db


if __name__ == "__main__":
    db = build_db()
