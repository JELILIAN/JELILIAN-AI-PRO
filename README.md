<p align="center">
  <img src="assets/logo.jpg" width="200"/>
</p>

English | [中文](README_zh.md) | [한국어](README_ko.md) | [日本語](README_ja.md)

[![GitHub stars](https://img.shields.io/github/stars/JELILIAN/JELILIAN-AI-PRO?style=social)](https://github.com/JELILIAN/JELILIAN-AI-PRO/stargazers)
&ensp;
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) &ensp;
[![Discord Follow](https://dcbadge.vercel.app/api/server/DYn29wFk9z?style=flat)](https://discord.gg/DYn29wFk9z)
[![Demo](https://img.shields.io/badge/Demo-Hugging%20Face-yellow)](https://huggingface.co/spaces/jelilian/JelilianAIProDemo)

# 👋 JELILIAN AI PRO

JELILIAN AI PRO is an incredible open-source framework for building general AI agents that can achieve any idea without limitations 🛫!

Our team is dedicated to creating powerful AI agents that can handle complex tasks through intelligent automation and advanced reasoning capabilities.

It's a comprehensive implementation with robust features, and we welcome any suggestions, contributions, and feedback!

Enjoy your own intelligent agent with JELILIAN AI PRO!

## Project Demo

Experience the power of JELILIAN AI PRO through our interactive demonstrations and real-world use cases.

## Installation

We provide two installation methods. Method 2 (using uv) is recommended for faster installation and better dependency management.

### Method 1: Using conda

1. Create a new conda environment:

```bash
conda create -n jelilian_ai_pro python=3.12
conda activate jelilian_ai_pro
```

2. Clone the repository:

```bash
git clone https://github.com/JELILIAN/JELILIAN-AI-PRO.git
cd JELILIAN-AI-PRO
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

### Method 2: Using uv (Recommended)

1. Install uv (A fast Python package installer and resolver):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone the repository:

```bash
git clone https://github.com/JELILIAN/JELILIAN-AI-PRO.git
cd JELILIAN-AI-PRO
```

3. Create a new virtual environment and activate it:

```bash
uv venv --python 3.12
source .venv/bin/activate  # On Unix/macOS
# Or on Windows:
# .venv\Scripts\activate
```

4. Install dependencies:

```bash
uv pip install -r requirements.txt
```

### Browser Automation Tool (Optional)
```bash
playwright install
```

## Configuration

JELILIAN AI PRO requires configuration for the LLM APIs it uses. Follow these steps to set up your configuration:

1. Create a `config.toml` file in the `config` directory (you can copy from the example):

```bash
cp config/config.example.toml config/config.toml
```

2. Edit `config/config.toml` to add your API keys and customize settings:

```toml
# Global LLM configuration
[llm]
model = "gpt-4o"
base_url = "https://api.openai.com/v1"
api_key = "sk-..."  # Replace with your actual API key
max_tokens = 4096
temperature = 0.0

# Optional configuration for specific LLM models
[llm.vision]
model = "gpt-4o"
base_url = "https://api.openai.com/v1"
api_key = "sk-..."  # Replace with your actual API key
```

## Quick Start

One line to run JELILIAN AI PRO:

```bash
python main.py
```

Then input your idea via terminal!

For MCP tool version, you can run:
```bash
python run_mcp.py
```

For unstable multi-agent version, you also can run:

```bash
python run_flow.py
```

### Custom Adding Multiple Agents

Currently, besides the general JELILIAN AI PRO Agent, we have also integrated the DataAnalysis Agent, which is suitable for data analysis and data visualization tasks. You can add this agent to `run_flow` in `config.toml`.

```toml
# Optional configuration for run-flow
[runflow]
use_data_analysis_agent = true     # Disabled by default, change to true to activate
```
In addition, you need to install the relevant dependencies to ensure the agent runs properly: [Detailed Installation Guide](app/tool/chart_visualization/README.md##Installation)

## How to contribute

We welcome any friendly suggestions and helpful contributions! Just create issues or submit pull requests.

**Note**: Before submitting a pull request, please use the pre-commit tool to check your changes. Run `pre-commit run --all-files` to execute the checks.

## Community Group
Join our networking group and share your experience with other developers!

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=JELILIAN/JELILIAN-AI-PRO&type=Date)](https://star-history.com/#JELILIAN/JELILIAN-AI-PRO&Date)

## Acknowledgement

Thanks to various open-source projects for providing foundational support for this project!

JELILIAN AI PRO is built by dedicated contributors. Huge thanks to the AI agent community!

## Cite
```bibtex
@misc{jelilianaiPro2025,
  author = {JELILIAN Team},
  title = {JELILIAN AI PRO: An open-source framework for building general AI agents},
  year = {2025},
  url = {https://github.com/JELILIAN/JELILIAN-AI-PRO},
}
```