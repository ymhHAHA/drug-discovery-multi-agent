from setuptools import setup, find_packages

setup(
    name="drug-discovery-multiagent",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="基于LangGraph的药物靶点发现多智能体系统",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/drug-discovery-multiagent",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "langgraph>=0.0.20",
        "langchain-core>=0.1.0",
        "dashscope>=1.14.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
    ],
)