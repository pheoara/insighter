from langchain_community.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from insighter.models.insight_prompts import (
    metadata_prompt,
    insight_def_prompt,
    text_to_sql_prompt,
    insight_prompt
)
from dotenv import load_dotenv
import os

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(temperature=0.9, model="gpt-3.5-turbo", openai_api_key=openai_api_key)

metadata_chain = LLMChain(llm=llm, prompt=metadata_prompt)
insight_def_chain = LLMChain(llm=llm, prompt=insight_def_prompt)
text_to_sql_chain = LLMChain(llm=llm, prompt=text_to_sql_prompt)
insight_chain = LLMChain(llm=llm, prompt=insight_prompt)


def get_metadata_result(columns):
    return metadata_chain.invoke({"columns": columns})

def get_insight_questions(metadata_result):
    return insight_def_chain.invoke({"metadata": metadata_result})

def get_sql_queries(metadata_result, insight_questions):
    return text_to_sql_chain.invoke({"metadata": metadata_result, "insight_questions": insight_questions})

def insights_creation(sql_queries_and_results):
    return insight_chain.invoke({"sql_queries_and_results": sql_queries_and_results})
