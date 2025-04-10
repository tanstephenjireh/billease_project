import tiktoken
from agents import function_tool
import pickle
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from flashrank import Ranker, RerankRequest

from agentss.collection_agent import collection_agent

import streamlit as st


tokenizer = tiktoken.get_encoding('cl100k_base')
# Create the length function
def tiktoken_len(text):
    tokens = tokenizer.encode(
        text,
        disallowed_special=()
    )
    return len(tokens)


def doc_to_pass(docs):
    # print("> doc_to_pass")
    passage_list = []
    for i, docs in enumerate(docs):
        passage_dic = {}
        passage_dic['id'] = i+1
        passage_dic['text'] = docs.page_content
        passage_dic['metadata'] = docs.metadata
        passage_list.append(passage_dic)
    return passage_list


def flash_rerank(user_query, passage_list):
    # print("> flash_rerank")
    ranker = Ranker(model_name="ms-marco-TinyBERT-L-2-v2")
    rerankrequest = RerankRequest(query=user_query, passages=passage_list)
    rank_results = ranker.rerank(rerankrequest)

    return rank_results


def retain_first_unique_source(text):
    # print("> retain_first_unique_source")
    lines = text.splitlines()
    seen_sources = set()
    output = []
    for line in lines:
        if line.startswith("source:"):
            source_url = line.strip()
            if source_url in seen_sources:
                continue  # skip repeated source
            seen_sources.add(source_url)
        output.append(line)
    return "\n".join(output)


@function_tool
def faq(query: str):
    """Contains answers about FAQs about how the product works on BillEase
    Use this tool when user asks specific questions about BillEase.
    """
    print("> faq")

    # Initialize the embeddings with text-ada-002 model
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    

    with open("faqs.pkl", "rb") as f:
        faqs = pickle.load(f)

    db = FAISS.from_documents(faqs, embeddings)
   
    docs = db.similarity_search(query, k=20)

    passage_list = doc_to_pass(docs)
    # print(passage_list)

    flashrank_ranked_result = flash_rerank(query, passage_list)
    # print(flashrank_ranked_result)
    flashrank_ranked_result = flashrank_ranked_result[0:10]
    # print(flashrank_ranked_result)

    contexts = [tx['text']+'\n'+'source: '+tx['metadata']['url']+'\n' for tx in flashrank_ranked_result]
    contexts = "\n".join(contexts)
    contexts = retain_first_unique_source(contexts)

    return contexts


faq_instruction = """Your name is Billy a helpful customer assistant of a company named BillEase. Remember to always
use the provided tools whenever possible. Do not rely on your own knowledge too much and instead
use your tools to help you answer queries. Make the response short, concise and in a fun tone and 
engaging for the customer. Make sure to give relevant source/s. Avoid fabricating references.
Do now answer outside of the context information given to you. Be honest if you are not sure or do not know the 
answer, advise to consult with a live customer agent or the relevant authorities.


This is the tool you have access to:
faq: Use this tool to answer questions about the FAQ of the company primarily about how the product works.

You can also hand off to specialists for collection of Promise To pay when needed, essentially this needs to collect 
the name of the customer first then the Promise to Pay date. Also to a specialist of processing transaction images.
"""


from agents import Agent

faqs_agent = Agent(
    name="FAQs Agent",
    instructions=faq_instruction,
    model="gpt-4o-mini",
    tools=[faq],  # note that we expect a list of tools
    handoffs=[collection_agent]
)