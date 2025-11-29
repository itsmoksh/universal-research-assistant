#Importing necessary libs

from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()
#Constants
CHUNK_SIZE = 1000
COLLECTION_NAME = "real_estate"
EMBEDDING_MODEL = 'Alibaba-NLP/gte-base-en-v1.5'

#global var
llm = None
vector_store = None

def initialize():
    global llm,vector_store
    if llm is None:
        llm = ChatGroq(model='llama-3.3-70b-versatile',temperature=0.7,max_tokens=700)

    if vector_store is None:
        ef = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"trust_remote_code": True}
        )
        vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            persist_directory= './resources/vectorstore',
            embedding_function=ef,
        )

def reset_vector_store():
    global vector_store
    vector_store.reset_collection()

def process_urls(urls):
    initialize()
    yield "Loading data from url"
    loader = WebBaseLoader(urls)
    data= loader.load()

    yield "Data loaded, Creating chunks"
    splitter = RecursiveCharacterTextSplitter(
        chunk_size= CHUNK_SIZE,
        separators= ["\n\n","\n","."," "],
        chunk_overlap=200
    )
    docs = splitter.split_documents(data)

    yield "Chunks created, storing in a vector store.."

    if docs:
        uuids = [str (uuid4()) for _ in range(len(docs))]
        vector_store.add_documents(docs,ids = uuids)


def generate(query):
    if not vector_store:
        raise RuntimeError("Vector store not initialized")
    results = vector_store.similarity_search(
        query,
        k=2,
    )
    sources = [result.metadata['source'] for result in results]
    pt = PromptTemplate.from_template('''Here is the retrieved context(chunks): {chunks} )
    Query: {query}
    Answer clearly using the above context,Do not generate preamble ''')

    chain = pt | llm
    sol = chain.invoke({'chunks':results,'query':query})
    return sol.content,sources

if __name__ == "__main__":
    pass



