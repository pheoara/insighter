from langchain.prompts import PromptTemplate

# =========================
# Metadata Extraction Agent Prompt
# ========================

metadata_prompt = PromptTemplate(
    input_variables=["columns"],
    template="""
*** Role ***: You are a data analyst.
*** Task ***: - You have been provided with a dataset containing sales and marketing data. 
              - Your goal is to read the instructions in the *** Instructions *** section below and extract metadata for each column in the dataset given in the *** Column Names *** section.

*** Column Names ***: 
 {columns}

*** Instructions ***:
1. For each column in the *** Column Names *** section,  provide:
    - A detailed metadata description including the data type.
    - Expected value ranges or categories. 
    - Relationships that might be derived from the column (e.g. dependencies, etc.).
2. You can assume that the dataset is clean and well-structured.
3. Your response should be in JSON format following the *** Output Format *** section provided below.


*** Output Format in Json ***:
{{
    "metadata": {{
        "column_name_1": {{
            "data_type": "Data type of the column (e.g., numerical, categorical, etc.)",
            "description": "Detailed description of the column including expected value ranges or categories, etc.",
            "relationships": ["relationship_1", "relationship_2"]
        }},
        "column_name_2": {{
            "data_type": "Data type of the column (e.g., numerical, categorical, etc.)",
            "description": "Detailed description of the column including expected value ranges or categories, etc.",
            "relationships": ["relationship_1", "relationship_2"]
        }},
        ...
    }}
}}
"""
)


# =========================
# Step 2: Insight Definition Agent Prompt
# =========================


insight_def_prompt = PromptTemplate(
    input_variables=["metadata"],
    template="""
*** Role ***: You are a data analyst.
*** Task ***: - You have been provided with a dataset containing metadata for sales and marketing data. 
              - Your goal is to read the instructions in the *** Instructions *** section below and formulate insight sql queries.

*** Metadata ***:
{metadata}

*** Instructions ***:
1. By Keeping in mind that these insights will later drive SQL queries:
    - Explore the metadata to surface a broad set of insights.
    - Focus on metrics like counts, percentages, averages, trends, ratios, rankings, growth rates, and distributions.
    - Keep queries clear, focused, and avoid large result sets.
    - Frame each insight as a specific, measurable statement.

2.Include diverse insights—predictive, diagnostic, deviations, profitability, loss, outliers, anomalies, normal patterns, etc.—using relevant metrics like rates, shares, variances, medians, percentiles, or other useful measures.
    - Example 1: Has support ticket volume increased significantly compared to the monthly average, if so, by how much?
    - Example 2: How much has revenue from new users changed compared to last month? Has there been a notable increase or decrease?

3. Your response should follow the *** Output Format *** provided below, providing a numbered list of the insight queries.

*** Output Format List ***:

1. Question 1
2. Question 2
...

"""
)

# =========================
# Step 3: Text-to-SQL Generation Agent Prompt
# =========================


text_to_sql_prompt = PromptTemplate(
    input_variables=["metadata", "instruction"],
    template="""
*** Role ***: You are a SQL query generator.
*** Task ***: - Yoy are provided with metadata for a dataset and a list of insight questions.
              - Your goal is to read the instructions in the *** Instructions *** section below and generate SQL queries to answer the insight questions based on the metadata provided in the *** Metadata *** section and the insight questions in the *** Insight Questions *** section.

*** Metadata ***:
{metadata}
*** Insight Questions ***:
{insight_questions}

*** Instructions ***:
1. For each insight question, generate a SQL query that can be used to answer the question. Keep in mind that we are using SQLite for this task.
2. Use the metadata provided to understand the dataset schema and formulate the SQL queries accordingly.
3. Ensure that SQL queries use valid, standard SQL syntax and functions, optimized for the given insight questions, and avoid unsupported functions like CORRELATION, COVARIANCE, STDEV, RANK(), ROW_NUMBER(), and others not supported by SQLite.
4. Your response should be in JSON format following the *** Output Format *** provided below.

*** Output Format in Json ***:
{{
    "sql_queries": {{
        "question_1": {{
            "insight_question": "Question 1",
            "sql_query": "",

        }},
        "question_2": {{
            "insight_question": "Question 2",
            "sql_query": ""
        }},
        ...
    }}
}}
"""
)

# =========================
# Insights Presentation Agent Prompt
# ========================

insight_prompt = PromptTemplate(
    input_variables=["sql_queries_and_results"],
    template="""
*** Role ***: You are a insights presenter.
*** Task ***: - You have been provided with the results of SQL queries generated to answer the insight questions using data provided in *** sql_queries_and_results *** section.
              - Your goal is to present the insights in a clear and concise manner.

*** sql_queries_and_results ***:
{sql_queries_and_results}

*** Instructions ***:
1. Review the results of the SQL queries and prepare a summary of the insights.
2. Focus on the key findings and trends that are relevant to the dataset.
3. Your response should be in a well-structured and readable format presenting the insights like they are being answered in a presentation.
4. Clearly explain each insight by stating what it reveals. If there's a trend, describe the nature of the trend; if there's a deviation, specify what differs and how.
5. Your response should be in JSON format following the *** Output Format *** provided below.

*** Output Format in JSON ***:
{{
  "insights": {{
    "question_1": [insight_1_summary],
    "question_2": [insight_2_summary],
    ...
  }}
}}
"""
)