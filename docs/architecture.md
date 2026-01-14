# Odoo AI Configurator - Architecture

## Overview

The Odoo AI Configurator is a modular system that enables AI-driven configuration of Odoo instances through natural language or declarative configs.

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│         (CLI / API / Natural Language)                   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              AI Orchestrator                             │
│  - Request interpretation                                │
│  - Agent selection                                       │
│  - Execution coordination                                │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬────────────┐
        │            │            │            │
        ▼            ▼            ▼            ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│ Company  │  │ Module   │  │ Product  │  │ Website  │
│ Agent    │  │ Agent    │  │ Agent    │  │ Agent    │
└────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │             │             │
     └─────────────┼─────────────┼─────────────┘
                   │             │
        ┌──────────┼─────────────┼──────────┐
        │          │             │          │
        ▼          ▼             ▼          ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│Integration│ │Automation│  │  User    │  │   MCP    │
│  Agent   │  │  Agent   │  │  Agent   │  │ Protocol │
└────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │             │             │
     └─────────────┼─────────────┼─────────────┘
                   │             │
                   ▼             ▼
         ┌─────────────────────────────┐
         │    Odoo XML-RPC Connector   │
         └─────────────┬───────────────┘
                       │
                       ▼
              ┌────────────────┐
              │ Odoo Instance  │
              └────────────────┘
```

## Components

### 1. Orchestrator
- **Purpose**: Coordinate agent execution
- **Responsibilities**:
  - Parse user requests
  - Select appropriate agents
  - Execute agents in correct order
  - Aggregate results

### 2. Agents
Each agent is specialized for a specific configuration domain:

#### CompanyAgent
- Configure company details
- Update contact information
- Set currency and localization

#### ModuleAgent
- Install/uninstall modules
- Manage dependencies
- Configure module settings

#### ProductAgent
- Import products from CSV
- Create product catalogs
- Manage inventory

#### WebsiteAgent
- Configure website settings
- Setup eCommerce
- Manage themes and pages

#### IntegrationAgent
- Configure external APIs
- Setup payment providers
- Configure shipping carriers

#### AutomationAgent
- Create automated actions
- Setup workflows
- Configure scheduled tasks

#### UserAgent
- Manage users
- Configure permissions
- Setup access rights

### 3. MCP Protocol
- **Purpose**: Enable AI interoperability
- **Features**:
  - Tool definitions
  - Capability discovery
  - Standardized communication

### 4. Connector
- **Purpose**: Communicate with Odoo
- **Technology**: XML-RPC
- **Operations**: CRUD operations on Odoo models

## Data Flow

1. **User Request** → Orchestrator
2. **Orchestrator** → Agent Selection
3. **Agents** → Odoo Connector
4. **Connector** → Odoo Instance
5. **Odoo** → Response
6. **Response** → User

## Extension Points

### Adding New Agents
1. Inherit from `OdooAgent`
2. Implement `can_handle()` and `execute()`
3. Register in Orchestrator

### Adding MCP Tools
1. Define tool in `MCPProtocol`
2. Map to agent in `MCPServer`
3. Update schema

## Configuration Methods

### 1. Natural Language
```python
orchestrator.configure("Setup eCommerce for bearings")
```

### 2. Declarative (YAML)
```yaml
company:
  name: "My Company"
modules:
  - website
  - crm
```

### 3. Programmatic
```python
orchestrator.configure("company", {
    'name': 'My Company',
    'email': 'info@company.com'
})
```

## Security

- Credentials stored securely
- XML-RPC over HTTPS
- User permissions respected
- Audit logging

## Performance

- Batch operations where possible
- Connection pooling
- Async execution (future)
- Caching (future)
