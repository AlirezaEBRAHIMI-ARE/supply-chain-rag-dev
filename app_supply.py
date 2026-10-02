# ============================================================
# Standard library imports
# ============================================================
import os
import shutil

# ============================================================
# Third-party imports
# ============================================================
from fastapi import FastAPI, HTTPException
# HTTPException lets us return proper error responses (like "404 not found")
# instead of crashing when something doesn't exist.

from tracking import init_db, insert_shipment, update_status, get_shipment
# These are the functions you already built and tested in tracking.py.
# Importing them here means app_supply.py can call them directly.

from pydantic import BaseModel
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from transformers import pipeline


# ============================================================
# 1. Build the RAG pipeline once, when the server starts
# ============================================================
file_paths = [
    "shipping_policy.txt",
    "returns_policy.txt",
    "customs_faq.txt",
    "order_tracking_faq.txt",
]

all_docs = []
for path in file_paths:
    loader = TextLoader(path)
    all_docs.extend(loader.load())

splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=40)
chunks = splitter.split_documents(all_docs)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

persist_directory = "./chroma_db"
if os.path.exists(persist_directory):
    shutil.rmtree(persist_directory)

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=persist_directory,
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

generator = pipeline(
    "text2text-generation",
    model="google/flan-t5-base",
)


def answer_question(question):
    retrieved_docs = retriever.invoke(question)
    context = "\n\n".join(chunk.page_content for chunk in retrieved_docs)
    prompt = f"""Answer the question using only the context below.

Context:
{context}

Question: {question}
Answer:"""

    response = generator(prompt, max_new_tokens=200)
    return response[0]["generated_text"]


app = FastAPI()
init_db()

class QuestionRequest (BaseModel):
    question: str

class UpdateStatusRequest(BaseModel):
    shipment_id: str
    new_status: str


class PredictDelayRequest(BaseModel):
    shipment_id: str


@app.post("/ask")

def ask(request: QuestionRequest):
    answer = answer_question(request.question)
    return {"question": request.question ,"answer":answer}

@app.get("/track/{shipment_id}")
def track(shipment_id: str):
    shipment = get_shipment(shipment_id)
    if shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment


@app.post("/update-status")
def update_status_endpoint(request: UpdateStatusRequest):
    try:
        update_status(request.shipment_id, request.new_status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return get_shipment(request.shipment_id)


@app.post("/predict-delay")
def predict_delay(request: PredictDelayRequest):
    # STUB: no real ML model here yet — this just returns a fixed fake value
    # so the endpoint exists and can be wired up/deployed/tested like a real one.
    return {"shipment_id": request.shipment_id, "predicted_delay_days": 1}