import gradio as gr
import pandas as pd
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_ollama import ChatOllama
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from pathlib import Path

# Global variables
spending_summary = None
vectorstore = None


def initialize_documents():
    """Load documents from the 'data' folder and initialize the vectorstore."""
    global vectorstore

    # Load all files in the data folder
    folder_path = Path('./data')
    files = [f.as_posix() for f in folder_path.rglob('*') if f.is_file()]
    docs = [TextLoader(file_path=fp, encoding='utf-8').load() for fp in files]
    docs_list = [item for sublist in docs for item in sublist]

    # Split documents for better retrieval
    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=7500, chunk_overlap=100)
    doc_splits = text_splitter.split_documents(docs_list)

    # Initialize the Chroma vectorstore
    vectorstore = Chroma.from_documents(
        documents=doc_splits,
        collection_name="rag-chroma",
        embedding=OllamaEmbeddings(model='nomic-embed-text'),
    )


def upload_csv(file):
    """Handle CSV upload and generate spending summary."""
    global spending_summary

    try:
        # Load the uploaded CSV file
        df = pd.read_csv(file.name)

        # Check for required columns
        required_columns = {'Category', 'Amount'}
        if not required_columns.issubset(df.columns):
            return "CSV must contain 'Category' and 'Amount' columns. Please upload a valid file."

        # Generate a spending summary
        spending_summary = "\n".join(f"{row['Category']}: {row['Amount']}" for _, row in df.iterrows())
        return "Spending data uploaded successfully! You can now ask questions about credit cards."
    except Exception as e:
        return f"Error processing the file: {e}"


def process_chat(messages, user_message):
    """Process user chat with the question and spending summary."""
    global spending_summary, vectorstore

    # Check if messages list is empty and add a welcome message if needed
    if not messages:
        messages = [{"role": "assistant", "content": "Hello! Please upload your spending details as a CSV file to get started."}]

    # Ensure spending data has been uploaded
    if spending_summary is None:
        return messages + [{"role": "assistant", "content": "Please upload your spending details as a CSV file first."}]

    # Ensure the vectorstore is initialized
    if vectorstore is None:
        return messages + [{"role": "assistant", "content": "Credit card data is not initialized. Please check the configuration."}]

    # Initialize the local model
    model_local = ChatOllama(model="mistral")

    # Define the RAG template
    after_rag_template = """Based only on the following context:
    User's Spending Details:
    {spending_details}

    Additional Context from Documents:
    {context}

    Question: {question}
    """
    after_rag_prompt = ChatPromptTemplate.from_template(after_rag_template)

    # Combine spending data with the question
    retriever = vectorstore.as_retriever()
    after_rag_chain = (
            {"spending_details": spending_summary, "context": retriever, "question": RunnablePassthrough()}
            | after_rag_prompt
            | model_local
            | StrOutputParser()
    )

    # Get the response
    try:
        response = after_rag_chain.invoke({"question": user_message})
    except Exception as e:
        response = f"An error occurred: {e}"

    # Append the response to the chat
    return messages + [{"role": "user", "content": user_message}, {"role": "assistant", "content": response}]


# Initialize documents during app startup
initialize_documents()

# Define Gradio Chat Interface
with gr.Blocks() as demo:
    gr.Markdown("## Credit Card Recommendation Chatbot")
    gr.Markdown(
        "Upload your spending details as a CSV file (with 'Category' and 'Amount' columns) and chat to get personalized credit card recommendations."
    )

    # File Upload Section
    with gr.Row():
        file_upload = gr.File(label="Upload Spending CSV", file_types=[".csv"])
        upload_result = gr.Textbox(label="Upload Status", interactive=False)

    # Chat Section
    chatbot = gr.Chatbot(label="Chat with the Credit Card Assistant", value=[])  # Initialize as empty list
    user_input = gr.Textbox(label="Your Message", placeholder="Type your question here...")
    send_button = gr.Button("Send")

    # Link functions to components
    file_upload.change(upload_csv, inputs=file_upload, outputs=upload_result)
    send_button.click(
        process_chat,
        inputs=[chatbot, user_input],  # Chatbot's current state and user's message
        outputs=chatbot,  # Update the chatbot's state
        queue=True,  # Process messages in order
    )


# Launch the Gradio interface
demo.launch(share=False)
