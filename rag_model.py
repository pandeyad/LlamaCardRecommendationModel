import gradio as gr
from langchain_community.document_loaders import WebBaseLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_community import embeddings
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.text_splitter import CharacterTextSplitter
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_community.document_loaders import DirectoryLoader
from multipart import file_path
import os
from pathlib import Path

from credit_card_url_provider import get_urls

folder_path = Path('./data')
files = [f.as_posix() for f in folder_path.rglob('*') if f.is_file()]
print(files)

# Which card will be best for me considering that I spend ~2L on online shopping, ~1 lakh on travelling and ~50K INR on groceries and other stuff.

def process_input(question):
    model_local = ChatOllama(model="mistral")

    # Convert string of URLs to list
    # urls_list = get_urls()
    # docs = [WebBaseLoader(url).load() for url in urls_list]
    docs = [TextLoader(file_path=fp, encoding='utf-8').load() for fp in files]
    docs_list = [item for sublist in docs for item in sublist]
    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=7500, chunk_overlap=100)
    doc_splits = text_splitter.split_documents(docs_list)

    vectorstore = Chroma.from_documents(
        documents=doc_splits,
        collection_name="rag-chroma",
        embedding=OllamaEmbeddings(model='nomic-embed-text'),
    )
    retriever = vectorstore.as_retriever()

    after_rag_template = """Answer the question based only on the following context:
    {context}
    Question: {question}
    """
    after_rag_prompt = ChatPromptTemplate.from_template(after_rag_template)
    after_rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | after_rag_prompt
            | model_local
            | StrOutputParser()
    )
    return after_rag_chain.invoke(question)

# Define Gradio interface
iface = gr.Interface(fn=process_input,
                     inputs=[gr.Textbox(label="Question")],
                     outputs="text",
                     title="Credit Card Recommendation ",
                     description="Enter the question to get started ")
iface.launch(share=False)