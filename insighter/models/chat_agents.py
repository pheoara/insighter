from langchain_community.chat_models import ChatOpenAI
from langchain.chains import LLMChain
import os
from insighter.utils.ai_client import get_client
from insighter.models.chat_prompts import router_prompt, sql_agent_prompt, alert_agent_prompt, visualization_agent_prompt, comparison_agent_prompt, insight_details_agent_prompt, casual_chat_agent_prompt
client = get_client()
openai_api_key = client.api_key if hasattr(client, 'api_key') else os.getenv("OPENAI_API_KEY")


llm = ChatOpenAI(temperature=0.9, model="gpt-3.5-turbo", openai_api_key=openai_api_key)

router_chain = LLMChain(llm=llm, prompt=router_prompt)
sql_chain = LLMChain(llm=llm, prompt=sql_agent_prompt)
alert_chain = LLMChain(llm=llm, prompt=alert_agent_prompt)
visualization_chain = LLMChain(llm=llm, prompt=visualization_agent_prompt)
comparison_chain = LLMChain(llm=llm, prompt=comparison_agent_prompt)
insight_details_chain = LLMChain(llm=llm, prompt=insight_details_agent_prompt)
casual_chat_chain = LLMChain(llm=llm, prompt=casual_chat_agent_prompt)



def route_query(user_query):
    return router_chain.invoke({"user_query": user_query})

def get_sql_query(user_query, columns):
    return sql_chain.invoke({"user_query": user_query, "columns": columns})

def get_alert(user_query, columns, insights):
    return alert_chain.invoke({"user_query": user_query, "columns": columns, "insights": insights})

def get_visualization(user_query, columns, csv_file, insights):
    return visualization_chain.invoke({"user_query": user_query, "columns": columns, "csv_file": csv_file, "insights": insights})
 
def get_compare_insights(user_query, insights):
    return comparison_chain.invoke({"user_query": user_query, "insights": insights})

def get_insight_details(user_query, metadata, insights):
    return insight_details_chain.invoke({"user_query": user_query, "metadata": metadata, "insights": insights}) 

def get_casual_chat(user_query, metadata):
    return casual_chat_chain.invoke({"user_query": user_query, "metadata": metadata})