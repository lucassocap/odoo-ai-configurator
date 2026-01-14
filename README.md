# 🤖 Odoo AI Configurator

AI-powered universal Odoo configuration system using MCP (Model Context Protocol).

## Features

- 🤖 **AI-Driven**: Natural language configuration
- 🔌 **MCP Protocol**: Works with any AI (Claude, GPT, Gemini)
- 🎯 **Modular Agents**: Specialized configuration agents
- 📋 **Complete Checklist**: 200+ configuration items
- 🚀 **Automated**: One-command setup
- 📝 **Declarative**: YAML configuration files

## Quick Start

```bash
# Install
pip install -e .

# Configure interactively
python scripts/run_configurator.py

# Or use YAML config
python scripts/run_configurator.py --config configs/examples/ecommerce.yaml
```

## Architecture

```
User Request → AI Orchestrator → Specialized Agents → Odoo
```

## Agents

- **CompanyAgent**: Company setup
- **ModuleAgent**: Module installation
- **ProductAgent**: Product management
- **WebsiteAgent**: Website/eCommerce
- **IntegrationAgent**: External integrations
- **AutomationAgent**: Workflow automation

## Example

```python
from odoo_ai_configurator import Orchestrator

orchestrator = Orchestrator("http://localhost:8069")
orchestrator.configure("Setup eCommerce store for bearings")
```

## License

MIT
