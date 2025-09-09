"""Setup configuration for Kasm MCP Server."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="kasm-mcp-server",
    version="2.0.0",
    author="RogueDev AI",
    author_email="contact@roguedev.ai",
    description="Model Context Protocol server for Kasm Workspaces integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/roguedev-ai/kasm-mcp-server",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "kasm-mcp-server=src.server:main",
        ],
    },
    package_data={
        "": ["*.md", "*.txt", ".env.example"],
    },
    include_package_data=True,
)
