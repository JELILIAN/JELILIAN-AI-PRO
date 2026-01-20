<p align="center">
  <img src="assets/logo.jpg" width="200"/>
</p>

[English](README.md) | 中文 | [한국어](README_ko.md) | [日本語](README_ja.md)

[![GitHub stars](https://img.shields.io/github/stars/JELILIAN/JELILIAN-AI-PRO?style=social)](https://github.com/JELILIAN/JELILIAN-AI-PRO/stargazers)
&ensp;
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) &ensp;

# 👋 JELILIAN AI PRO

JELILIAN AI PRO 是一个令人惊叹的开源框架，用于构建通用AI代理，可以实现任何想法而无需限制 🛫！

我们的团队致力于创建强大的AI代理，能够通过智能自动化和高级推理能力处理复杂任务。

这是一个功能强大的综合实现，我们欢迎任何建议、贡献和反馈！

使用 JELILIAN AI PRO 享受您自己的智能代理！

## 项目演示

通过我们的交互式演示和真实世界用例体验 JELILIAN AI PRO 的强大功能。

## 安装

我们提供两种安装方法。推荐使用方法2（使用uv），以获得更快的安装速度和更好的依赖管理。

### 方法1：使用conda

1. 创建新的conda环境：

```bash
conda create -n jelilian_ai_pro python=3.12
conda activate jelilian_ai_pro
```

2. 克隆仓库：

```bash
git clone https://github.com/JELILIAN/JELILIAN-AI-PRO.git
cd JELILIAN-AI-PRO
```

3. 安装依赖：

```bash
pip install -r requirements.txt
```

### 方法2：使用uv（推荐）

1. 安装uv（快速的Python包安装器和解析器）：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. 克隆仓库：

```bash
git clone https://github.com/JELILIAN/JELILIAN-AI-PRO.git
cd JELILIAN-AI-PRO
```

3. 创建新的虚拟环境并激活：

```bash
uv venv --python 3.12
source .venv/bin/activate  # 在Unix/macOS上
# 或在Windows上：
# .venv\Scripts\activate
```

4. 安装依赖：

```bash
uv pip install -r requirements.txt
```

### 浏览器自动化工具（可选）
```bash
playwright install
```

## 配置

JELILIAN AI PRO 需要配置其使用的LLM API。按照以下步骤设置配置：

1. 在`config`目录中创建`config.toml`文件（可以从示例复制）：

```bash
cp config/config.example.toml config/config.toml
```

2. 编辑`config/config.toml`添加您的API密钥并自定义设置：

```toml
# 全局LLM配置
[llm]
model = "gpt-4o"
base_url = "https://api.openai.com/v1"
api_key = "sk-..."  # 替换为您的实际API密钥
max_tokens = 4096
temperature = 0.0

# 特定LLM模型的可选配置
[llm.vision]
model = "gpt-4o"
base_url = "https://api.openai.com/v1"
api_key = "sk-..."  # 替换为您的实际API密钥
```

## 快速开始

一行命令运行 JELILIAN AI PRO：

```bash
python main.py
```

然后通过终端输入您的想法！

对于MCP工具版本，您可以运行：
```bash
python run_mcp.py
```

对于不稳定的多代理版本，您也可以运行：

```bash
python run_flow.py
```

## 如何贡献

我们欢迎任何友好的建议和有用的贡献！只需创建问题或提交拉取请求。

**注意**：在提交拉取请求之前，请使用pre-commit工具检查您的更改。运行`pre-commit run --all-files`执行检查。

## 社区群组
加入我们的网络群组，与其他开发者分享您的经验！

## 星标历史

[![Star History Chart](https://api.star-history.com/svg?repos=JELILIAN/JELILIAN-AI-PRO&type=Date)](https://star-history.com/#JELILIAN/JELILIAN-AI-PRO&Date)

## 致谢

感谢各种开源项目为此项目提供基础支持！

JELILIAN AI PRO 由专门的贡献者构建。非常感谢AI代理社区！

## 引用
```bibtex
@misc{jelilianaiPro2025,
  author = {JELILIAN Team},
  title = {JELILIAN AI PRO: 构建通用AI代理的开源框架},
  year = {2025},
  url = {https://github.com/JELILIAN/JELILIAN-AI-PRO},
}
```