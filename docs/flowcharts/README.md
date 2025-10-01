# 📊 Diagramas del Proyecto QA Test Generator

Esta carpeta contiene los diagramas de flujo del proyecto en formato PNG y sus fuentes en formato de texto (Mermaid).

## 🎯 Contenido del Directorio

### 📊 Diagramas de Arquitectura y Flujos

#### 1. Arquitectura General
- **Archivo**: `arquitectura_general.md`
- **Descripción**: Vista de alto nivel de todos los componentes del sistema con diagrama Mermaid

#### 2. Flujo de Usuario - Historias de Usuario
- **Archivo**: `flujo_user_story.md`
- **Descripción**: Proceso interactivo de generación y modificación de historias de usuario

#### 3. Flujo de Usuario - Casos de Prueba
- **Archivo**: `flujo_test_cases.md`
- **Descripción**: Proceso interactivo de generación y modificación de casos de prueba

#### 4. Flujo Completo de Datos
- **Archivo**: `flujo_completo_datos.md`
- **Descripción**: Camino completo de los datos desde entrada hasta salida

#### 5. Sistema de Agentes IA
- **Archivo**: `sistema_agentes_ia.md`
- **Descripción**: Arquitectura del sistema de integración con APIs de IA

#### 6. Patrón Abstract Factory
- **Archivo**: `patron_abstract_factory.md`
- **Descripción**: Implementación del patrón Abstract Factory para agentes IA

### 📚 Documentación Técnica

#### 7. Código Detallado
- **Archivo**: `codigo_detallado.md`
- **Descripción**: Explicación completa línea por línea de todo el código fuente
- **Audiencia**: Desarrolladores junior que necesitan entender el proyecto
- **Contenido**: Arquitectura, patrones de diseño, flujos de trabajo, utilidades, CLI, etc.

## 🖼️ Diagramas en PNG - ✅ TODOS CORREGIDOS Y FUNCIONANDO

**¡Problema resuelto!** Todos los diagramas han sido corregidos eliminando caracteres especiales y texto en español que causaban errores de parsing en mermaidchart.

### ✅ Diagramas Completamente Funcionales:
- `arquitectura_general.md` - ✅ Sin emojis, sintaxis limpia
- `flujo_user_story.md` - ✅ State diagram en inglés
- `flujo_test_cases.md` - ✅ State diagram en inglés
- `flujo_completo_datos.md` - ✅ Graph simplificado
- `sistema_agentes_ia.md` - ✅ Subgraphs en inglés
- `patron_abstract_factory.md` - ✅ Class diagram limpio

### 🔧 Correcciones Aplicadas:
- **Eliminé caracteres especiales**: ñ, acentos, emojis, ¿, ¡
- **Traduje al inglés**: Todo el texto de los diagramas
- **Simplifiqué sintaxis**: Nombres de nodos más limpios
- **Corregí transiciones**: Eliminé descripciones problemáticas en state diagrams
- **Corregí encoding**: Solo caracteres ASCII estándar

Para generar las imágenes PNG:

### 📋 Lista de Diagramas Disponibles

| Diagrama | Archivo Markdown | Descripción |
|----------|------------------|-------------|
| 🏗️ Arquitectura General | `arquitectura_general.md` | Vista completa del sistema |
| 👤 Flujo User Story | `flujo_user_story.md` | Workflow de historias de usuario |
| 🧪 Flujo Test Cases | `flujo_test_cases.md` | Workflow de casos de prueba |
| 🔄 Flujo Completo Datos | `flujo_completo_datos.md` | Flujo end-to-end completo |
| 🤖 Sistema Agentes IA | `sistema_agentes_ia.md` | Arquitectura de agentes IA |
| 🏭 Abstract Factory | `patron_abstract_factory.md` | Patrón de diseño implementado |

## 🛠️ Cómo Generar PNG desde los Diagramas

Cada archivo `.md` contiene bloques de código Mermaid. Para convertirlos a PNG:

### Opción 1: Mermaid CLI (Recomendado)
```bash
# Instalar CLI de Mermaid
npm install -g @mermaid-js/mermaid-cli

# Convertir un diagrama específico
mmdc -i docs/flowcharts/arquitectura_general.md -o docs/flowcharts/arquitectura_general.png

# Convertir todos los flowcharts
for file in docs/flowcharts/*.md; do
    base=$(basename "$file" .md)
    mmdc -i "$file" -o "docs/diagramas/${base}.png"
done
```

### Opción 2: Editor Online (Fácil)
1. Ve a https://mermaid.live/
2. Copia el contenido del bloque ```mermaid``` de cualquier archivo `.md`
3. Haz clic en "Export" → "Download PNG"

### Opción 3: VS Code con Extensiones
1. Instala extensión "Mermaid Preview" o "Markdown Preview Mermaid Support"
2. Abre el archivo `.md` en VS Code
3. Usa la opción de exportar imagen del preview

### Opción 4: Script Automático
```bash
#!/bin/bash
# script: generate_diagrams.sh
mkdir -p docs/flowcharts/png

for md_file in docs/flowcharts/*.md; do
    if [ "$md_file" != "docs/diagramas/README.md" ] && [ "$md_file" != "docs/diagramas/codigo_detallado.md" ]; then
        base_name=$(basename "$md_file" .md)
        echo "Generando PNG para: $base_name"
        mmdc -i "$md_file" -o "docs/diagramas/png/${base_name}.png" -t dark -b transparent
    fi
done

echo "✅ Todos los diagramas PNG generados en docs/diagramas/png/"
```

## 📊 Resultado Esperado

Después de ejecutar cualquiera de las opciones anteriores, tendrás:

```
docs/diagramas/
├── png/                          # 🆕 NUEVO DIRECTORIO
│   ├── arquitectura_general.png
│   ├── flujo_user_story.png
│   ├── flujo_test_cases.png
│   ├── flujo_completo_datos.png
│   ├── sistema_agentes_ia.png
│   └── patron_abstract_factory.png
├── *.md                          # Archivos fuente
└── README.md                     # Este archivo
```

## 🎨 Estilos de los Diagramas

Los diagramas usan estilos consistentes:
- **Colores temáticos** por componente
- **Flechas direccionales** claras
- **Notas explicativas** en nodos importantes
- **Layout automático** optimizado

## 📖 Documentación Relacionada

- `codigo_detallado.md` - Explicación completa del código
- `../USER_MANUAL.md` - Manual de usuario
- `../MANUAL_USUARIO.md` - Manual de usuario en español
- `../architecture.md` - Documentación técnica de arquitectura

## 📚 Documentación Relacionada

- `CODIGO_DETALLADO.md` - Explicación detallada de todo el código
- `../USER_MANUAL.md` - Manual de usuario
- `../MANUAL_USUARIO.md` - Manual de usuario en español
- `../architecture.md` - Documentación técnica de arquitectura