# Odoo Modules Reference

Complete list of Odoo modules supported by the configurator.

## Usage

You can install modules using friendly names or technical names:

```python
# Friendly names
orchestrator.configure("modules", {
    'modules': ['ecommerce', 'crm', 'inventory']
})

# Technical names
orchestrator.configure("modules", {
    'modules': ['website_sale', 'crm', 'stock']
})
```

## Supported Modules

### Website & eCommerce
| Friendly Name   | Technical Name | Description     |
| --------------- | -------------- | --------------- |
| website         | website        | Website Builder |
| ecommerce, shop | website_sale   | Online Store    |
| blog            | website_blog   | Blog            |
| forum           | website_forum  | Forum           |
| slides          | website_slides | eLearning       |
| events          | website_event  | Events          |
| livechat        | im_livechat    | Live Chat       |

### Sales & CRM
| Friendly Name     | Technical Name    | Description          |
| ----------------- | ----------------- | -------------------- |
| crm               | crm               | CRM                  |
| sales, quotations | sale_management   | Sales                |
| subscriptions     | sale_subscription | Subscriptions        |
| rental            | sale_renting      | Rental               |
| coupons           | sale_coupon       | Coupons & Promotions |
| loyalty           | loyalty           | Loyalty Program      |

### Inventory & Manufacturing
| Friendly Name        | Technical Name  | Description   |
| -------------------- | --------------- | ------------- |
| inventory, warehouse | stock           | Inventory     |
| manufacturing, mrp   | mrp             | Manufacturing |
| plm                  | mrp_plm         | PLM           |
| quality              | quality_control | Quality       |
| maintenance          | maintenance     | Maintenance   |
| barcode              | stock_barcode   | Barcode       |

### Accounting & Finance
| Friendly Name | Technical Name    | Description |
| ------------- | ----------------- | ----------- |
| accounting    | account           | Accounting  |
| invoicing     | account_invoicing | Invoicing   |
| expenses      | hr_expense        | Expenses    |
| assets        | account_asset     | Assets      |
| budget        | account_budget    | Budget      |

### Point of Sale
| Friendly Name      | Technical Name | Description   |
| ------------------ | -------------- | ------------- |
| pos, point of sale | point_of_sale  | Point of Sale |
| restaurant         | pos_restaurant | Restaurant    |

### Human Resources
| Friendly Name | Technical Name | Description |
| ------------- | -------------- | ----------- |
| hr, employees | hr             | Employees   |
| recruitment   | hr_recruitment | Recruitment |
| appraisals    | hr_appraisal   | Appraisals  |
| attendance    | hr_attendance  | Attendance  |
| timesheet     | hr_timesheet   | Timesheets  |
| payroll       | hr_payroll     | Payroll     |
| fleet         | fleet          | Fleet       |

### Project Management
| Friendly Name  | Technical Name | Description |
| -------------- | -------------- | ----------- |
| project, tasks | project        | Project     |
| helpdesk       | helpdesk       | Helpdesk    |

### Marketing
| Friendly Name    | Technical Name       | Description          |
| ---------------- | -------------------- | -------------------- |
| marketing        | marketing_automation | Marketing Automation |
| email marketing  | mass_mailing         | Email Marketing      |
| sms marketing    | mass_mailing_sms     | SMS Marketing        |
| social marketing | social_media         | Social Media         |
| surveys          | survey               | Surveys              |

### Productivity
| Friendly Name | Technical Name | Description |
| ------------- | -------------- | ----------- |
| calendar      | calendar       | Calendar    |
| contacts      | contacts       | Contacts    |
| documents     | documents      | Documents   |
| sign          | sign           | Sign        |
| approvals     | approvals      | Approvals   |
| voip          | voip           | VoIP        |

### Services
| Friendly Name | Technical Name | Description   |
| ------------- | -------------- | ------------- |
| field service | industry_fsm   | Field Service |
| appointments  | appointment    | Appointments  |

### Purchase
| Friendly Name       | Technical Name       | Description         |
| ------------------- | -------------------- | ------------------- |
| purchase            | purchase             | Purchase            |
| purchase agreements | purchase_requisition | Purchase Agreements |

### Other
| Friendly Name | Technical Name | Description        |
| ------------- | -------------- | ------------------ |
| iot           | iot            | Internet of Things |
| studio        | web_studio     | Studio             |

## Examples

### Install eCommerce Suite
```python
orchestrator.configure("modules", {
    'modules': [
        'website',
        'ecommerce',
        'payment',
        'delivery',
        'inventory'
    ]
})
```

### Install Complete Business Suite
```python
orchestrator.configure("modules", {
    'modules': [
        'crm',
        'sales',
        'inventory',
        'accounting',
        'project',
        'hr'
    ]
})
```

### Install Manufacturing Suite
```python
orchestrator.configure("modules", {
    'modules': [
        'manufacturing',
        'inventory',
        'quality',
        'maintenance',
        'plm'
    ]
})
```

## YAML Configuration

```yaml
modules:
  # eCommerce
  - website
  - ecommerce
  - payment
  
  # Business
  - crm
  - sales
  - accounting
  
  # Operations
  - inventory
  - manufacturing
  - quality
```

## Adding Custom Modules

If you need to install a module not in the map, use the technical name directly:

```python
orchestrator.configure("modules", {
    'modules': ['my_custom_module']
})
```
