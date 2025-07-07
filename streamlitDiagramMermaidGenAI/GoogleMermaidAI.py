# --- Librerías Estándar de Python ---
# base64 y os son parte de la librería estándar de Python y no requieren instalación adicional.
import base64
import os

# --- Google Generative AI (Gemini): Para la generación de contenido con IA ---
# Es el SDK oficial de Google para interactuar con sus modelos de lenguaje generativos, como Gemini.
# Lo usaremos para enviar el prompt del usuario al modelo y recibir el código Mermaid generado.
# Comando para instalar: pip install google-generativeai
from google import genai
from google.genai import types

# --- Streamlit: Framework principal para la aplicación web ---
# Aunque este es el módulo de backend, importa Streamlit para dos funciones clave:
# 1. @st.cache_resource: Para cachear la conexión con la API y mejorar el rendimiento.
# 2. st.secrets: Para acceder de forma segura a la clave de la API.
# Comando para instalar: pip install streamlit
import streamlit as st

def corregirMermaid(mermaid_code: str) -> str:
    """
    Realiza correcciones menores en el código Mermaid generado por la IA.

    A menudo, los modelos de IA pueden generar pequeñas inconsistencias sintácticas, como espacios
    indebidos antes o después de guiones bajos o corchetes. Esta función "limpia" el código
    para asegurar que sea compatible con el renderizador de MermaidJS.

    Args:
        mermaid_code (str): El código Mermaid en bruto generado por la IA.

    Returns:
        str: El código Mermaid corregido y listo para ser renderizado.
    """
    # Reemplaza secuencias de espacio y guion bajo para unificar la sintaxis.
    mermaid_code = mermaid_code.replace(" \_", "\_")
    # Elimina espacios antes de un corchete de apertura, común en las etiquetas de enlaces.
    mermaid_code = mermaid_code.replace(" [", "[")
    # Reemplaza secuencias de guion bajo y espacio.
    mermaid_code = mermaid_code.replace("\_ ", "\_")
    # Imprime el código corregido en la consola para fines de depuración.
    print(mermaid_code)
    return mermaid_code

# --- Caché de Streamlit ---
# @st.cache_resource es un decorador de Streamlit que le indica a la aplicación que
# guarde en memoria el resultado de esta función. En este caso, cachea el cliente de la API de Google.
# Esto es muy eficiente porque evita tener que establecer una nueva conexión con la API
# cada vez que el usuario interactúa con la aplicación.
@st.cache_resource
def generarDiagrama(prompt: str) -> str:
    """
    Genera código de diagrama Mermaid a partir de un prompt de usuario utilizando la API de Google Gemini.

    Esta función se conecta a la API de Google, envía el prompt del usuario junto con un conjunto
    detallado de instrucciones (system prompt) que guía al modelo para que genere una respuesta
    precisa y en el formato correcto. La respuesta se recibe en streaming.

    Args:
        prompt (str): La descripción en lenguaje natural del diagrama que el usuario quiere crear.

    Returns:
        str: Una cadena de texto con el código Mermaid generado por la IA, ya corregido.
    """
    # Inicializa el cliente de la API de Google.
    # Utiliza st.secrets para obtener la clave de la API de forma segura desde los secretos de Streamlit.
    # ¡Nunca escribas tus claves de API directamente en el código!
    client = genai.Client(
        api_key=st.secrets["GOOGLE_API_KEY"],
    )
    
    # Selecciona el modelo de IA a utilizar. "gemini-2.5-flash-preview-04-17" es un modelo rápido y eficiente.
    model = "gemini-2.5-flash-preview-04-17"
    
    # Prepara el contenido que se enviará al modelo, asignando el rol de "user" al prompt del usuario.
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        )       
    ]
    
    # Configuración avanzada para la generación de contenido.
    generate_content_config = types.GenerateContentConfig(
        # `thinking_budget=0` podría instruir al modelo a responder más directamente sin pasos intermedios.
        thinking_config=types.ThinkingConfig(
            thinking_budget=0,
        ),
        # Especifica que queremos una respuesta en texto plano.
        response_mime_type="text/plain",
        # --- System Instruction (Prompt Engineering Avanzado) ---
        # Esta es la parte más importante. Le damos al modelo un "rol" y un "contexto" muy detallados
        # para que se comporte exactamente como queremos. Le proporcionamos una "hoja de trucos" (cheat sheet)
        # de la sintaxis de Mermaid para que sus respuestas sean precisas y se adhieran a las reglas.
        # Esta técnica se conoce como "in-context learning" o RAG (Retrieval-Augmented Generation) manual.
        system_instruction=[
            types.Part.from_text(text="""**Situation**
Un usuario requiere la generación de un gráfico o diagrama utilizando el lenguaje de marcado Mermaid, con el objetivo de crear representaciones visuales de información estructurada de manera precisa y directa.

**Task**
Generar código Mermaid para el diagrama o gráfico solicitado, proporcionando únicamente el código necesario para su procesamiento en Mermaid, sin incluir explicaciones, comentarios o texto adicional.

**Objective**
Producir un resultado limpio y funcional que pueda ser directamente implementado en un renderizador de Mermaid, facilitando la visualización rápida y eficiente de la estructura o relación solicitada.

**Knowledge**
- Utilizar únicamente sintaxis válida de Mermaid
- Omitir cualquier texto explicativo o de contexto
- Generar código que sea inmediatamente procesable
- Mantener la precisión y claridad en la representación visual
Extracted text from https://jojozhuang.github.io/tutorial/mermaid-cheat-sheet/: [1]

# Mermaid Cheat Sheet

Cheat Sheet for Mermaid.

## 1. Flowcharts

A flowchart is a type of diagram that represents an algorithm, workflow or process. The flowchart shows the steps as boxes of various kinds, and their order by connecting the boxes with arrows. This diagrammatic representation illustrates a solution model to a given problem.

### 1.1 Graph

Possible directions are:

*   TB - top bottom
*   BT - bottom top
*   RL - right left
*   LR - left right
*   TD - same as TB

| Direction | Diagram Definition |
| :-------- | :----------------- |
| TB        | `graph TB; A-->B;` |
| BT        | `graph BT; A-->B;` |
| RL        | `graph RL; A-->B;` |
| LR        | `graph LR; A-->B;` |
| TD        | `graph TD; A-->B;` |

### 1.2 Nodes & shapes

| Feature               | Diagram Definition                                  |
| :-------------------- | :-------------------------------------------------- |
| Node(Default)         | `graph LR; id;`                                     |
| Node with Text        | `graph LR; id1[This is the text in the box]`        |
| Node with Round Edges | `graph LR; id1(This is the text in the box)`        |
| Node in Circle Form   | `graph LR; id1((This is the text in the circle))`   |
| Node in Asymmetric Shape | `graph LR; id1>This is the text in the box]`    |
| Node in Rhombus Form  | `graph LR; id1{This is the text in the box}`        |

### 1.3 Links Between Nodes

| Feature                       | Diagram Definition                |
| :---------------------------- | :-------------------------------- |
| Link with Arrow Head          | `graph LR; A-->B`                 |
| Open Link                     | `graph LR; A---B`                 |
| Text on Links(1)              | `graph LR; A-- This is the text ---B` |
| Text on Links(2)              | `graph LR; A---|This is the text|B` |
| Link with Arrow Head and Text(1)| `graph LR; A-->|text|B`          |
| Link with Arrow Head and Text(2)| `graph LR; A-- text -->B`         |
| Dotted Link                   | `graph LR; A-.->B;`               |
| Dotted Link with Text         | `graph LR; A-. text .-> B`        |
| Thick Link                    | `graph LR; A ==> B`               |
| Thick link with text          | `graph LR; A == text ==> B`       |

### 1.4 Subgraphs

Syntax:

```
subgraph title
graph definition
end
```

Example:

```mermaid
graph TB
c1-->a2
subgraph one
a1-->a2
end
subgraph two
b1-->b2
end
subgraph three
c1-->c2
end
```

## 2. Sequence Diagrams

A Sequence diagram is an interaction diagram that shows how processes operate with one another and in what order. [1]

### 2.1 Participants

The participants or actors are rendered in order of appearance in the diagram source text. [1]

```mermaid
sequenceDiagram
participant Alice
participant John
Alice->>John: Hello John, how are you?
John-->>Alice: Great!
```

You can specify the actor's order of appearance to show the participants in a different order. [1]

```mermaid
sequenceDiagram
participant John
participant Alice
Alice->>John: Hello John, how are you?
John-->>Alice: Great!
```

The participants can be defined implicitly without specifying them with the participant keyword. [1]

```mermaid
sequenceDiagram
Alice->>John: Hello John, how are you?
John-->>Alice: Great!
```

### 2.2 Aliases

The participant can have a convenient identifier and a descriptive label. [1]

```mermaid
sequenceDiagram
participant A as Alice
participant J as John
A->>J: Hello John, how are you?
J-->>A: Great!
```

### 2.3 Messages

Messages can be of two displayed either solid or with a dotted line. [1]

`[Actor][Arrow][Actor]:Message text` [1]

There are six types of arrows currently supported: [1]

| Arrow Type | Description                      |
| :--------- | :------------------------------- |
| `->`       | Solid line without arrow         |
| `–>`       | Dotted line without arrow        |
| `-»`       | Solid line with arrowhead        |
| `–»`       | Dotted line with arrowhead       |
| `-x`       | Solid line with a cross at the end (async) |
| `–x`       | Dotted line with a cross at the end (async) |

### 2.4 Activations

Activate and deactivate an actor. [1]

```mermaid
sequenceDiagram
Alice->>John: Hello John, how are you?
activate John
John-->>Alice: Great!
deactivate John
```

Shortcut notation by appending `+/-` suffix to the message arrow. [1]

```mermaid
sequenceDiagram
Alice->>+John: Hello John, how are you?
John-->>-Alice: Great!
```

Activations can be stacked for same actor: [1]

```mermaid
sequenceDiagram
Alice->>+John: Hello John, how are you?
Alice->>+John: John, can you hear me?
John-->>-Alice: Hi Alice, I can hear you!
John-->>-Alice: I feel great!
```

### 2.5 Notes

Add notes to a sequence diagram by the notation `Note <location> <actors>: Text in note content`. [1]

`Note [ right of | left of | over ] [Actor]: Text in note content` [1]

1) Right Side [1]

```mermaid
sequenceDiagram
participant John
Note right of John: Text in note
```

2) Left Side [1]

```mermaid
sequenceDiagram
participant John
Note left of John: Text in note
```

3) Over [1]

```mermaid
sequenceDiagram
participant John
Note over John: Text in note
```

4) Create notes spanning two participants [1]

```mermaid
sequenceDiagram
Alice->>John: Hello John, how are you?
Note over Alice,John: A typical interaction
```

### 2.6 Loops

Express loops in a sequence diagram by the notation `loop <text> ... end`. [1]

```mermaid
loop Loop text
... statements ...
end
```

Example: [1]

```mermaid
sequenceDiagram
Alice->John: Hello John, how are you?
loop Every minute
John-->Alice: Great!
end
```

### 2.7 Alt

Express alternative paths in a sequence diagram by the notation `alt <text> ... else ... end`. [1]

```mermaid
alt Describing text
... statements ...
else
... statements ...
end
```

Or, if there is sequence that is optional (if without else). [1]

```mermaid
opt Describing text
... statements ...
end
```

Example: [1]

```mermaid
sequenceDiagram
Alice->>John: Hello John, how are you?
alt is sick
John->>Alice: Not so good :(
else is well
John->>Alice: Feeling fresh like a daisy
end
opt Extra response
John->>Alice: Thanks for asking
end
```

## 3. Gant Diagrams

A Gantt chart is a type of bar chart, first developed by Karol Adamiecki in 1896, and independently by Henry Gantt in the 1910s, that illustrates a project schedule. Gantt charts illustrate the start and finish dates of the terminal elements and summary elements of a project. [1]

```mermaid
gantt
title A Gantt Diagram
dateFormat YYYY-MM-DD
section Section
First Task :a1, 2018-07-01, 30d
Another Task :after a1, 20d
section Another
Second Task :2018-07-12, 12d
Third Task : 24d
```

```mermaid
gantt dateFormat YYYY-MM-DD title Adding GANTT diagram functionality to mermaid section A section Completed task :done, des1, 2018-01-06,2018-01-08 Active task :active, des2, 2018-01-09, 3d Future task : des3, after des2, 5d Future task2 : des4, after des3, 5d section Critical tasks Completed task in the critical line :crit, done, 2018-01-06,24h Implement parser and jison :crit, done, after des1, 2d Create tests for parser :crit, active, 3d Future task in critical line :crit, 5d Create tests for renderer :2d Add to mermaid :1d section Documentation Describe gantt syntax :active, a1, after des1, 3d Add gantt diagram to demo page :after a1 , 20h Add another diagram to demo page :doc1, after a1 , 48h section Last section Describe gantt syntax :after doc1, 3d Add gantt diagram to demo page :20h Add another diagram to demo page :48h
```

## 4. Demos

### 4.1 Basic Flowchart

```mermaid
graph LR
A[Square Rect] -- Link text --> B((Circle))
A --> C(Round Rect)
B --> D{Rhombus}
C --> D
```

### 4.2 Flowchart with Decision

```mermaid
graph TD
A[Christmas] -->|Get money| B(Go shopping)
B --> C{Let me think}
C -->|One| D[Laptop]
C -->|Two| E[iPhone]
C -->|Three| F[fa:fa-car Car]
```

### 4.3 Larger Flowchart with Some Styling

```mermaid
graph TB
sq[Square shape] --> ci((Circle shape))
subgraph A
od>Odd shape]-- Two line<br/>edge comment --> ro
di{Diamond with <br/> line break} -.-> ro(Rounded<br>square<br>shape)
di==>ro2(Rounded square shape)
end
%% Notice that no text in shape are added here instead that is appended further down
e --> od3>Really long text with linebreak<br>in an Odd shape]
%% Comments after double percent signs
e((Inner / circle<br>and some odd <br>special characters)) --> f(,.?!+-*ز)
cyr[Cyrillic]-->cyr2((Circle shape Начало));

classDef green fill:#9f6,stroke:#333,stroke-width:2px
classDef orange fill:#f96,stroke:#333,stroke-width:4px
class sq,e green
class di orange
```

### 4.4 Basic Sequence Diagram

```mermaid
sequenceDiagram
Alice ->> Bob: Hello Bob, how are you?
Bob-->>John: How about you John?
Bob--x Alice: I am good thanks!
Bob-x John: I am good thanks!
Note right of John: Bob thinks a long<br/>long time, so long<br/>that the text does<br/>not fit on a row.
Bob-->Alice: Checking with John...
Alice->John: Yes... John, how are you?
```

### 4.5 Message to Self in Loop

```mermaid
sequenceDiagram
participant Alice
participant Bob
Alice->>John: Hello John, how are you?
loop Healthcheck
John->>John: Fight against hypochondria
end
Note right of John: Rational thoughts<br/>prevail...
John-->>Alice: Great!
John->>Bob: How about you?
Bob-->>John: Jolly good!
```
### 4.5 Entity Relationship Diagram

erDiagram
    CLIENTE {
        int id_cliente PK
        varchar  nombre
        varchar direccion
        varchar telefono
    }

    PRODUCTO {
        int id_producto PK
        varchar nombre_producto
        decimal precio
        int stock
    }

    VENTA {
        int id_venta PK
        int id_cliente FK
        datetime fecha
        decimal total
    }

    DETALLE_VENTA {
        int id_detalle_venta PK
        int id_venta FK
        int id_producto  FK
        int cantidad
        decimal precio_unitario
        decimal subtotal
    }

    CLIENTE ||--o{ VENTA : "realiza"
    VENTA ||--|{ DETALLE_VENTA  : "contiene"
    PRODUCTO ||--o{ DETALLE_VENTA : "es_parte_de"
    
**Constraints**
- No añadir ningún texto fuera del código Mermaid
- Respetar estrictamente la estructura del diagrama solicitado
- Garantizar que el código generado sea sintácticamente correcto
- Los nombres de diagramas no deben contener espacios, respetar los nombres de los diagramas del knowledge
- Utilizar únicamente sintaxis válida de Mermaid
- Los nombres de campos o variables no deben contener espacios, utilizar guiones bajos o camelCase
- Evitar cualquier tipo de anotación o comentario"""),
        ],
    )
    
    # Inicializa una cadena vacía para almacenar el resultado.
    resultado = ""
    
    # --- Procesamiento en Streaming ---
    # `generate_content_stream` devuelve la respuesta de la IA en "trozos" (chunks) a medida que se genera.
    # Esto mejora la percepción de velocidad, ya que no hay que esperar a que se genere toda la respuesta.
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        # Concatena cada trozo de texto a la variable resultado.
        resultado = f"{resultado}{chunk.text}"
        
    # Una vez recibida toda la respuesta, la pasa por la función de corrección y la devuelve.
    return corregirMermaid(resultado)