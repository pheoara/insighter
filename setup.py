from setuptools import setup, find_packages

setup(
    name="insighter",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "streamlit",
        "pandas",
        "matplotlib",
        "langchain",
        "openai",
        "langgraph",
        "pydantic",
        "sqlalchemy",
        "python-dotenv",
    ],
    author="Ammara Amin",
    author_email="ammaramin08@gmail.com",
    description="Insighter - Data Analysis and Insights Tool",
    keywords="streamlit, data analysis, insights",
    url="https://github.com/pheoara/insighter",
) 