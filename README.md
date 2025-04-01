# Insighter - Data Analysis And Insights Tool

Insighter is a comprehensive data analysis and insights generation tool built with Streamlit. It is designed to empower data analysts, business users, and developers by enabling them to upload datasets, generate actionable insights automatically, and interact with the system via a chatbot. The tool leverages a combination of in-memory SQLite databases, custom AI agents, and data processing pipelines to transform raw data into meaningful insights without the need for extensive coding.

![Insighter workflow](picture.png)

---

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Project Structure](#project-structure)
4. [Installation](#installation)
5. [Running the Application](#running-the-application)
6. [Development & Architecture](#development--architecture)
   - [Chat Workflow Pipeline](#chat-workflow-pipeline)
   - [Insight Generation Pipeline](#insight-generation-pipeline)
7. [AI Agent Prompts](#ai-agent-prompts)

---

## Introduction

Insighter is built to simplify data analysis by automating the process of extracting insights from structured data. Whether you are looking to perform quick exploratory data analysis or need detailed insights to inform business decisions, Insighter offers an intuitive interface and powerful backend pipelines to handle complex queries and generate visualizations, alerts, and comparisons—all powered by AI.

---

## Features

- **Data Upload & Integration:** Upload CSV files and load them into an in-memory SQLite database.
- **Automated Insights:** Automatically extract metadata, define insight questions, generate SQL queries, and compile results into actionable insights.
- **Chatbot Interaction:** Engage with a chatbot that routes your natural language queries to the appropriate processing pipelines.
- **Dynamic Visualizations:** Generate Python code for visualizations using Matplotlib with a consistent Streamlit theme.
- **Alert System:** Create custom alerts based on data thresholds or conditions.
- **Modular Design:** Easily extend or modify functionality with clearly separated pipelines and agent modules.
- **Streamlit UI & State Management:** Built entirely with Streamlit, including UI components, page navigation, and session state management for a seamless user experience.

---

## Project Structure

The project is organized into several directories, each with a specific role:

```
insighter/
├── components/     # UI components
├── config/         # Configuration files
├── data/           # Data files and database
├── models/         # AI models and prompts
├── pages/          # Application pages
├── pipelines/      # Data processing pipelines
├── styles/         # CSS and styling
└── utils/          # Utility functions
```

Each folder contributes to a modular design that separates UI, configuration, data handling, and backend logic.

---

## Installation

To install the required dependencies, run the following command:

```bash
pip install -r requirements.txt
```

---

## Running The Application

Launch the application using Streamlit by executing:

```bash
streamlit run app.py
```

This command starts the web interface, allowing you to upload datasets and interact with the tool.

---

## Development & Architecture

Insighter’s architecture is built around two main pipelines that work in tandem to process user queries and generate insights.

### Chat Workflow Pipeline

The chat workflow is designed to handle real-time user queries by following these steps:

1. **Load Data:**  
   The `load_csv_to_sql_node` function reads CSV files from the current project and loads them into an in-memory SQLite database.

2. **Extract Metadata:**  
   The `extract_metadata_node` inspects the SQLite database to retrieve table names and column details using SQLite’s PRAGMA commands.

3. **Route Query:**  
   The `route_query_node` leverages an AI router agent to analyze the user’s query and determine the required action (e.g., SQL query, alert, visualization, etc.).

4. **Branch Node:**  
   Depending on the routed action, the `branch_node` delegates the query to the appropriate processing function:
   - **SQL Query Execution:** Constructs and executes SQL queries via the `sql_node`.
   - **Alert Generation:** Creates custom alerts using the `alert_node`.
   - **Visualization:** Generates and executes visualization code through the `visualization_node`.
   - **Insight Comparison:** Compares multiple insights using the `comparison_node`.
   - **Insight Details:** Provides further information, context, or visualizability status using the `insight_details_node`.
   - **Casual Chat:** Handles conversational queries with the `casual_chat_node`.

This modular approach ensures that each query is handled efficiently based on its context.

### Insight Generation Pipeline

For in-depth insights, Insighter employs a separate pipeline that includes:

1. **Data Loading & Metadata Extraction:**  
   Reads the CSV file, loads data into SQLite, and extracts metadata about table structures.

2. **Defining Insights:**  
   The `define_insights_node` formulates insight questions by analyzing metadata. This step helps identify key metrics and trends for analysis.

3. **SQL Query Generation:**  
   The `generate_sql_node` utilizes an AI model to generate SQL queries for each insight question based on the extracted metadata.

4. **Executing SQL Queries:**  
   The `execute_sql_queries_node` executes the generated SQL queries and collects the results from the database.

5. **Insights Presentation:**  
   Finally, the `generate_insights_node` and `present_final_insights_node` process the query results to create a comprehensive set of insights that are presented to the user.

---

## AI Agent Prompts

### Prompts Used in Chat Pipeline

- **Router Agent Prompt:** Determines which action to perform (e.g., chat, SQL, visualization, alert, etc.).
- **SQL Agent Prompt:** Generates SQL queries from natural language based on metadata.
- **Alert Agent Prompt:** Produces concise, actionable alert messages.
- **Visualization Agent Prompt:** Generates Python code to visualize data or insights.
- **Insight Comparison Prompt:** Compares multiple insights for trends, differences, or similarities.
- **Insight Details Prompt:** Explains visualizability, context, or query details behind specific insights.
- **Casual Chat Prompt:** Handles small talk and data-related conversation in a friendly tone.

### Prompts Used in Insight Generation Pipeline

- **Metadata Extraction Prompt:** Generates rich metadata (types, ranges, relationships) for each column.
- **Insight Definition Prompt:** Crafts analytical questions based on metadata.
- **Text-to-SQL Prompt:** Transforms insight questions into valid, executable SQL queries.
- **Insight Presentation Prompt:** Converts SQL results into presentation-ready insight summaries.


---

## Conclusion

Insighter provides a robust foundation for turning raw data into valuable insights. Its modular design, comprehensive pipelines, and intelligent AI agents make it a powerful tool for anyone looking to derive meaningful insights from their data. Built entirely with Streamlit, it offers a modern, responsive UI with efficient state management built in.

