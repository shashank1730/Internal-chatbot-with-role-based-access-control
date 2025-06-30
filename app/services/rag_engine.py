from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain_ollama import OllamaLLM
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_experimental.agents import create_csv_agent
from langchain.schema import Document
import os
import pandas as pd

# --- Configs ---
DATA_PATHS = {
    "engineering": "resources/data/engineering",
    "finance": "resources/data/finance",
    "hr": "resources/data/hr",
    "marketing": "resources/data/marketing",
    "general": "resources/data/general",
    "C-Level Executives":["resources/data/engineering", "resources/data/finance", "resources/data/hr", "resources/data/marketing", "resources/data/general"]
}
csv_agents = {}

# --- Helpers ---
def is_structured_query(query: str) -> bool:
    keywords = ["total", "average", "sum", "minimum", "maximum", "count", "salary", "revenue", "expenses", "amount", "table", "csv", "leaves"]
    return any(kw in query.lower() for kw in keywords)

def find_matching_csv(role: str, query: str, data_paths: dict) -> str | None:
    if role == "C-Level Executives":
        for role in data_paths:
            if role=="C-Level Executives":
                continue
            print(role)
            folder = data_paths.get(role.lower())
            if not folder:
                
                return None
            for file in os.listdir(folder):
                if file.endswith(".csv"):
                    
                    path = folder + f"/{file}"
                    print(path)
                    try:
                        print("--try---")
                        df = pd.read_csv(path, nrows=1)
                        print(df.head())
                        print(col.lower() in query.lower() for col in df.columns)
                        if any(col.lower() in query.lower() for col in df.columns):
                            print("-----")
                            return file
                    except:
                        continue
        return None
    else:
        folder = data_paths.get(role.lower())
        if not folder:
            return None
        for file in os.listdir(folder):
            if file.endswith(".csv"):
                path = os.path.join(folder, file)
                try:
                    df = pd.read_csv(path, nrows=1)
                    if any(col.lower() in query.lower() for col in df.columns):
                        return file
                except:
                    continue
        return None

def verify_with_llm(summary: str, original_query: str) -> bool:
    llm = OllamaLLM(model="llama3.2", temperature=0)
    validation_prompt = PromptTemplate.from_template(
        """
        Given the user query and a structured data summary (from a CSV analysis), determine if the summary answers the user's intent clearly and directly.

        Summary:
        {summary}

        User Question:
        {query}

        Reply with just YES if the summary is good enough and directly answers the question, else reply NO.
        """
    )
    prompt = validation_prompt.format(summary=summary, query=original_query)
    result = llm.invoke(prompt).strip().lower()
    print("$$$$$$$$",result,"$$$$$$$$$$")
    return "# output: yes" in result

def load_csv_agents(data_paths: dict) -> dict:
    agents = {}
    llm = OllamaLLM(model="llama3.2", temperature=0)
    for role, folder in data_paths.items():
        if role == "C-Level Executives":
            for sub_folder in folder:
                for file in os.listdir(sub_folder):
                    if file.endswith(".csv"):
                        path = os.path.join(sub_folder, file)
                        key = f"{role}:{file}"
                        try:
                            agents[key] = create_csv_agent(llm, path, verbose=True, allow_dangerous_code=True,     
                                                           prompt=PromptTemplate.from_template("""
                                                               You are a strict data analyst. ONLY use the data from the dataframe provided.
                                                                NEVER make assumptions or guesses. If the answer cannot be directly derived, say "Not available in data".

                                                                {input}
                                                             """)
                                                            )
                        except Exception as e:
                            print(f"❌ Failed to load CSV agent for {key}: {e}")
            continue
        if not os.path.exists(folder):
            continue
        


        for file in os.listdir(folder):
            if file.endswith(".csv"):
                path = os.path.join(folder, file)
                key = f"{role}:{file}"
                try:
                    agents[key] = create_csv_agent(llm, path, verbose=True, allow_dangerous_code=True)
                except Exception as e:
                    print(f"❌ Failed to load CSV agent for {key}: {e}")
    return agents

def get_rag_response(query: str, role: str) -> tuple[str, list]:
    global csv_agents
    if not csv_agents:
        csv_agents = load_csv_agents(DATA_PATHS)

    csv_file = find_matching_csv(role, query, DATA_PATHS)
    if csv_file:
        print(f"CSV file found for this {role}")
        print(csv_file)
        agent_key = f"{role}:{csv_file}"
        print("----",agent_key)
        if agent_key in csv_agents:
            
            try:
                summary = csv_agents[agent_key].invoke(query)
                print(f"📊 CSV Agent Result: {summary}")
                print(verify_with_llm(summary,query))
                if verify_with_llm(summary, query):
                    return summary, [{"file_name": csv_file, "link": "#"}]
            except Exception as e:
                print(f"⚠️ CSV Agent error: {e}")

    # VectorDB fallback
    print("🔁 Falling back to VectorDB")
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
        - If the answer is not explicitly or reasonably inferable, reply: "The provided documents do not contain this information."
    """)
    document_chain = create_stuff_documents_chain(llm, prompt)

    db = Chroma(
        persist_directory="resources/vectorstore",
        embedding_function=HuggingFaceEmbeddings(
            model_name="nomic-ai/nomic-embed-text-v1",
            model_kwargs={"trust_remote_code": True},
            cache_folder="./models"
        )
    )

    role_access = {
        "engineering": ["engineering", "general"],
        "finance": ["finance", "general"],
        "hr": ["hr", "general"],
        "marketing": ["marketing", "general"],
        "C-Level Executives" :["engineering", "finance", "hr","marketing"]
    }
    allowed_docs = role_access.get(role.lower(), [])
    if allowed_docs:
        search_kwargs = {"filter": {"role": {"$in": allowed_docs}}, "k": 5}
    else:
        search_kwargs = {"k": 5}

    retriever = db.as_retriever(search_kwargs=search_kwargs)


    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    response = retrieval_chain.invoke({"input": query, "role": role})

    docs = retriever.get_relevant_documents(query)
    sources = []
    for doc in docs:
        source_path = doc.metadata.get("source")
        if source_path:
            file_name = os.path.basename(source_path)
            link = f"http://localhost:8000/files/{'/'.join(source_path.split(os.sep)[-2:])}"
        else:
            file_name = "Unknown"
            link = "#"
        sources.append({"file_name": file_name, "link": link})

    return response["answer"], sources
