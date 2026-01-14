# Odoo AI Configurator - Lessons Learned

## Bug: Odoo 17/18 XML-RPC API IndexError

**Fecha**: 2026-01-14
**Severidad**: CRÍTICA
**Afecta**: Odoo 17.0, 18.0

### Descripción
El API XML-RPC de Odoo 17 y 18 tiene un bug que causa `IndexError: tuple index out of range` en operaciones `search()`.

### Error Exacto
```python
File: /usr/lib/python3/dist-packages/odoo/osv/expression.py, line 265
Error: IndexError: tuple index out of range
elif token[1] == 'in' and not (isinstance(token[2], Query) or token[2]):
```

### Impacto
- ❌ No se pueden buscar registros via XML-RPC
- ❌ No se pueden instalar módulos programáticamente
- ❌ No se pueden verificar productos existentes
- ❌ Afecta ModuleAgent, ProductAgent, WebsiteConfigAgent

### Workaround
**Solución temporal**: Usar XML-RPC directo sin el wrapper de búsqueda

```python
# ❌ NO FUNCIONA (causa IndexError)
models.execute_kw(db, uid, password, 
    'product.template', 'search', 
    [[('default_code', '=', sku)]]
)

# ✅ FUNCIONA (crear directamente)
product_id = models.execute_kw(db, uid, password,
    'product.template', 'create',
    [product_data]
)
```

### Lección Aprendida
Para proyectos de cliente, crear scripts **standalone** que:
1. Usen XML-RPC directo sin búsquedas
2. No dependan del framework MCP completo
3. Sean portables y fáciles de ejecutar
4. Manejen errores gracefully

### Aplicado en
- `scripts/import_products_standalone.py` - Script standalone para importar productos
- Proyecto Bearings Inc - Cliente usa script independiente

### Recomendación
Mantener dos versiones:
1. **MCP Agents** - Para desarrollo y testing
2. **Standalone Scripts** - Para producción y clientes

---

## Validación de Productos

**Fecha**: 2026-01-14
**Categoría**: MEJORA

### Implementación
Agregada validación completa en `WebsiteConfigAgent._validate_products()`:

```python
def _validate_products(self, products: List[Dict]) -> tuple:
    # Validaciones:
    - SKU requerido
    - Nombre requerido
    - Precio válido (no negativo)
    - Imagen existe y formato válido
    - Descripción mínimo 10 caracteres
    - Categoría requerida
```

### Beneficios
- ✅ Previene errores antes de importar
- ✅ Reporta problemas específicos
- ✅ Mejora experiencia de usuario
- ✅ Reduce debugging time

### Lección
**SIEMPRE validar datos antes de operaciones costosas** (como importar a base de datos)

---

## Proyecto de Cliente Separado

**Fecha**: 2026-01-14
**Categoría**: ARQUITECTURA

### Decisión
Separar proyectos de cliente del framework MCP:

```
TradingAgents-main/
├── odoo/
│   └── odoo-ai-configurator/    # Framework MCP
└── bearings/                     # Cliente: Bearings Inc
    ├── .git/                     # Repo independiente
    └── ...
```

### Razones
1. **Independencia**: Cliente no depende del framework
2. **Simplicidad**: Más fácil de mantener
3. **Portabilidad**: Fácil de clonar y usar
4. **Git separado**: Historial limpio por proyecto

### Lección
**Separar framework de implementaciones de cliente** para mejor mantenibilidad

---

## WebsiteConfigAgent

**Fecha**: 2026-01-14
**Categoría**: AGENTE NUEVO

### Funcionalidades
- Importar productos con validación
- Configurar tema (colores, layout)
- Setup categorías
- Configurar homepage
- Integración con memoria

### Lección
El agente está bien diseñado pero **requiere workaround para Odoo 17/18** debido al bug XML-RPC.

Para producción, usar scripts standalone hasta que Odoo fixee el bug.

---

## Resumen de Lecciones

1. ✅ **Validar siempre** antes de operaciones costosas
2. ✅ **Separar framework de clientes** para mejor arquitectura
3. ⚠️ **Odoo 17/18 tienen bugs** - usar workarounds
4. ✅ **Scripts standalone** son mejores para producción
5. ✅ **Documentar bugs** y workarounds para futuros proyectos
