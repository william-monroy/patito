# Documentación Compilador Patito

## Índice

1. [Introducción](#introducción)
2. [Estructura del Proyecto](#estructura-del-proyecto)
3. [Visión General del Compilador](#visión-general-del-compilador)
   - 3.1. [Análisis Léxico](#31-análisis-léxico)
   - 3.2. [Análisis Sintáctico](#32-análisis-sintáctico)
   - 3.3. [Análisis Semántico](#33-análisis-semántico)
   - 3.4. [Generación de Código Intermedio](#34-generación-de-código-intermedio)
4. [Descripción Detallada de los Componentes](#descripción-detallada-de-los-componentes)
   - 4.1. [Lexer y Parser Generados por ANTLR](#41-lexer-y-parser-generados-por-antlr)
   - 4.2. [Listener Personalizado (`PatitoCustomListener.py`)](#42-listener-personalizado-patitocustomlistenerpy)
   - 4.3. [Archivo Principal (`main_patito.py`)](#43-archivo-principal-main_patitopy)
5. [Estructuras de Datos Utilizadas](#estructuras-de-datos-utilizadas)
   - 5.1. [Directorios y Tablas](#51-directorios-y-tablas)
   - 5.2. [Pilas](#52-pilas)
6. [Flujo de Ejecución del Compilador](#flujo-de-ejecución-del-compilador)
7. [Análisis de un Ejemplo de Ejecución](#análisis-de-un-ejemplo-de-ejecución)


---

## Introducción

Este documento proporciona una descripción completa del proyecto "Compilador Patito", un compilador que procesa un lenguaje de programación simple llamado Patito. El objetivo es explicar detalladamente cómo funciona el proyecto, cómo se relacionan sus componentes y proporcionar una definición de cada función clave en el código.

---

## Estructura del Proyecto

El proyecto se compone de los siguientes archivos y componentes principales:

- **Gramática ANTLR:**
  - `Patito.g4`: Archivo de gramática que define la sintaxis del lenguaje Patito.
- **Generados por ANTLR:**
  - `PatitoLexer.py`: Analizador léxico generado por ANTLR.
  - `PatitoParser.py`: Analizador sintáctico generado por ANTLR.
  - `PatitoListener.py`: Clase base para el listener generado por ANTLR.
- **Listener Personalizado:**
  - `PatitoCustomListener.py`: Implementación personalizada del listener para realizar el análisis semántico y la generación de código intermedio.
- **Archivo Principal:**
  - `main_patito.py`: Archivo que coordina la ejecución del compilador.
- **Código Fuente de Entrada:**
  - `main.patito`: Archivo con el código fuente en lenguaje Patito que será procesado por el compilador.

---

## Visión General del Compilador

El compilador Patito sigue las fases típicas de un compilador:

1. **Análisis Léxico:** Convierte la secuencia de caracteres de entrada en una secuencia de tokens.
2. **Análisis Sintáctico:** Analiza la secuencia de tokens para construir un árbol de sintaxis abstracta (AST) basado en la gramática del lenguaje.
3. **Análisis Semántico:** Verifica la coherencia semántica del código, como tipos de datos y declaraciones de variables.
4. **Generación de Código Intermedio:** Produce una representación intermedia del código (cuádruplos) que puede ser utilizada para la ejecución o traducción adicional.

### 3.1. Análisis Léxico

El **analizador léxico** convierte el código fuente en una secuencia de tokens. Utiliza las reglas definidas en el archivo `Patito.g4` para identificar:

- **Identificadores:** Nombres de variables y funciones.
- **Números:** Literales numéricos enteros y flotantes.
- **Operadores y Símbolos Especiales:** Como `+`, `-`, `*`, `/`, `(`, `)`, etc.
- **Palabras Reservadas:** Como `programa`, `vars`, `entero`, `flotante`, `si`, `sino`, `mientras`, `escribe`, etc.

### 3.2. Análisis Sintáctico

El **analizador sintáctico** utiliza la secuencia de tokens para construir un árbol de sintaxis abstracta (AST) que representa la estructura gramatical del código fuente. Se asegura de que el código siga las reglas sintácticas del lenguaje Patito.

### 3.3. Análisis Semántico

El **analizador semántico** verifica la coherencia y validez del código en términos de tipos de datos, declaración y uso de variables, parámetros de funciones, etc. Se encarga de:

- **Verificar Declaraciones:** Asegurar que las variables y funciones estén declaradas antes de ser usadas.
- **Compatibilidad de Tipos:** Verificar que las operaciones se realicen entre tipos compatibles.
- **Ámbitos:** Manejar los diferentes ámbitos (global y local) de variables y funciones.

### 3.4. Generación de Código Intermedio

El compilador genera una representación intermedia del código en forma de **cuádruplos**, que son tuplas que representan operaciones de bajo nivel, facilitando la interpretación o traducción posterior.

---

## Descripción Detallada de los Componentes

### 4.1. Lexer y Parser Generados por ANTLR

- **ANTLR (Another Tool for Language Recognition)** es una herramienta que genera analizadores léxicos y sintácticos a partir de una gramática especificada.
- **Archivo `Patito.g4`:** Contiene la gramática del lenguaje Patito, definiendo sus reglas léxicas y sintácticas.
- **Generación de Código:** ANTLR toma `Patito.g4` y genera `PatitoLexer.py`, `PatitoParser.py` y `PatitoListener.py`, que son utilizados en el proyecto.

### 4.2. Listener Personalizado (`PatitoCustomListener.py`)

Este es el corazón del análisis semántico y la generación de código intermedio. Hereda de `PatitoListener` y sobreescribe métodos para reaccionar a eventos específicos durante el recorrido del AST.

#### Funciones y Métodos Principales:

1. **`__init__(self)`:** Constructor que inicializa todas las estructuras de datos necesarias:

   - **`directorio_funciones`:** Diccionario que almacena información de las funciones definidas.
   - **`tabla_variables_global`:** Tabla de variables en el ámbito global.
   - **`tabla_variables_actual`:** Tabla de variables del ámbito actual.
   - **`funcion_actual`:** Nombre de la función actual en contexto.
   - **`pila_scopes`:** Pila que maneja los diferentes ámbitos.
   - **`cubo_semantico`:** Estructura que define las reglas de compatibilidad de tipos y operaciones.
   - **Pilas para operandos, operadores, tipos y saltos (`pila_operandos`, `pila_operadores`, `pila_tipos`, `pila_saltos`).
   - **Contadores y listas auxiliares para temporales y cuádruplos.

2. **Manejo de Variables:**

   - **`enterD(self, ctx)`:** Maneja la declaración de variables. Agrega variables a la tabla de variables actual y verifica si ya han sido declaradas.
   - **`enterAsigna(self, ctx)`:** Verifica si la variable a la que se le asignará un valor ha sido declarada.

3. **Manejo de Funciones:**

   - **`enterFuncs(self, ctx)`:** Inicia el proceso de declaración de una nueva función. Crea un nuevo ámbito, maneja los parámetros y agrega la función al directorio de funciones.
   - **`exitFuncs(self, ctx)`:** Finaliza el ámbito de la función actual y agrega el cuádruplo `ENDFUNC`.

4. **Generación de Cuádruplos:**

   - **`exitAsigna(self, ctx)`:** Genera el cuádruplo de asignación, verificando la compatibilidad de tipos.
   - **`exitExp(self, ctx)`:** Genera cuádruplos para operaciones aritméticas (`+`, `-`).
   - **`exitTermino(self, ctx)`:** Genera cuádruplos para operaciones de multiplicación y división (`*`, `/`).
   - **`exitExpresion(self, ctx)`:** Genera cuádruplos para expresiones lógicas y maneja condicionales y ciclos.

5. **Manejo de Condicionales y Ciclos:**

   - **`enterCondicion(self, ctx)`:** Indica el inicio de una estructura condicional.
   - **`exitCondicion(self, ctx)`:** Maneja el fin de una estructura condicional, ajustando los cuádruplos de salto.
   - **`enterE_c(self, ctx)`:** Maneja el bloque `sino` dentro de una condición.
   - **`enterCiclo(self, ctx)`:** Marca el inicio de un ciclo `mientras`.
   - **`exitCiclo(self, ctx)`:** Ajusta los cuádruplos al finalizar un ciclo.

6. **Manejo de Impresión:**

   - **`enterImprime(self, ctx)`:** Prepara la lista para almacenar los parámetros de impresión.
   - **`exitImprime(self, ctx)`:** Genera los cuádruplos `PRINT` en el orden correcto.
   - **`exitParam_imp(self, ctx)`:** Recolecta los parámetros que se van a imprimir.

7. **Manejo de Llamadas a Funciones:**

   - **`enterLlamada(self, ctx)`:** Inicia el proceso de una llamada a función, verificando si la función existe.
   - **`exitLlamada(self, ctx)`:** Genera cuádruplos para pasar los parámetros y realiza la llamada (`GOSUB`).
   - **`exitE_l(self, ctx)`:** Recolecta los parámetros pasados en la llamada a la función.

8. **Utilidades y Auxiliares:**

   - **`obtener_tipo_variable(self, nombre_var)`:** Devuelve el tipo de una variable dado su nombre.
   - **`inicializar_cubo_semantico(self)`:** Inicializa el cubo semántico con las reglas de compatibilidad de tipos.
   - **`es_expresion_de_condicion(self, ctx)`:** Determina si una expresión es parte de una condición.
   - **`es_expresion_de_ciclo(self, ctx)`:** Determina si una expresión es parte de un ciclo.

#### Estructura Interna:

- **Directorios y Tablas:**

  - **`directorio_funciones`:** Almacena información sobre las funciones, como su tipo de retorno, parámetros, tabla de variables y el índice de inicio en los cuádruplos.
  - **`tabla_variables_global` y `tabla_variables_actual`:** Gestionan las variables declaradas en el ámbito global y el ámbito actual.

- **Pilas:**

  - **`pila_operandos`:** Almacena los operandos utilizados en las expresiones.
  - **`pila_operadores`:** Almacena los operadores encontrados en las expresiones.
  - **`pila_tipos`:** Almacena los tipos de los operandos.
  - **`pila_saltos`:** Maneja los índices de los cuádruplos que requieren ajustes de dirección (como en condicionales y ciclos).
  - **`pila_parametros`:** Almacena los parámetros pasados en una llamada a función.

### 4.3. Archivo Principal (`main_patito.py`)

Este archivo coordina la ejecución del compilador:

1. **Lectura del Archivo de Entrada:**

   - Verifica que se proporcione el archivo de código fuente.
   - Utiliza `FileStream` para leer el archivo.

2. **Análisis Léxico y Sintáctico:**

   - Crea una instancia del lexer y del parser utilizando los generados por ANTLR.
   - Genera el árbol de sintaxis abstracta (AST).

3. **Análisis Semántico y Generación de Cuádruplos:**

   - Crea una instancia de `PatitoCustomListener`.
   - Utiliza `ParseTreeWalker` para recorrer el AST y aplicar el listener personalizado.

4. **Gestión de Errores:**

   - Si hay errores sintácticos o semánticos, los muestra y finaliza la ejecución.

5. **Salida de Resultados:**

   - Si no hay errores, muestra el directorio de funciones, las tablas de variables y los cuádruplos generados.

---

## Estructuras de Datos Utilizadas

### 5.1. Directorios y Tablas

- **Directorio de Funciones (`directorio_funciones`):** Diccionario que almacena información clave sobre las funciones:

  ```python
  {
      'nombre_funcion': {
          'tipo_retorno': 'tipo',
          'parametros': [ {'nombre': 'param1', 'tipo': 'tipo'}, ... ],
          'tabla_variables': { 'nombre_var': {'tipo': 'tipo'}, ... },
          'cuadruplos_inicio': índice_del_cuádruplo_de_inicio
      },
      ...
  }
    ```
- **Tabla de Variables Global (`tabla_variables_global`):** Almacena las variables declaradas en el ámbito global.

- **Tabla de Variables Actual (`tabla_variables_actual`):** Referencia a la tabla de variables del ámbito actual (global o de una función).

### 5.2. Pilas

- **Pila de Operandos (`pila_operandos`):** Almacena los operandos encontrados en las expresiones.

- **Pila de Operadores (`pila_operadores`):** Almacena los operadores.

- **Pila de Tipos (`pila_tipos`):** Almacena los tipos de los operandos.

- **Pila de Saltos (`pila_saltos`):** Utilizada para manejar las direcciones de salto en estructuras de control como condicionales y ciclos.

- **Pila de Parámetros (`pila_parametros`):** Almacena los parámetros pasados en una llamada a función.

---

## Flujo del Compilador

1. **Inicio:** El usuario ejecuta `python main_patito.py main.patito`.

2. **Lectura del Código Fuente:** El archivo `main.patito` es leído y procesado.

3. **Análisis Léxico:** El lexer convierte el código fuente en una secuencia de tokens.

4. **Análisis Sintáctico:** El parser construye el árbol de sintaxis abstracta (AST) del programa.

5. **Análisis Semántico y Generación de Cuádruplos:**
    - Listener Personalizado: `PatitoCustomListener` recorre el AST.
    - Declaraciones y Definiciones: Se procesan las declaraciones de variables y funciones, construyendo las tablas y directorios. 
    - Expresiones y Operaciones: Se manejan las expresiones, utilizando las pilas para operandos y operadores, y generando cuádruplos. 
    - Estructuras de Control: Se manejan condicionales y ciclos, utilizando la pila de saltos para manejar las direcciones de los cuádruplos.
6. **Finalización:** Si no hay errores, se muestra el directorio de funciones, las tablas de variables y los cuádruplos generados.

---

## Análisis de un Ejemplo de Ejecución

Supongamos que el archivo main.patito contiene el siguiente código:

```patito
programa miPrograma;
vars
    x, y : entero;
    z : flotante;
    holi: entero;

nula miFuncion(c: entero, a: entero) {
    vars
        pi: flotante;
    {
        pi = 3.14;
        c = a + 10;
        escribe("El valor de c es: ", c);
    }
};

inicio{
    x = 10;
    y = 20;
    z = x + y * 1.5;
    si (x > y) {
        escribe("x es mayor que y");
    } sino {
        escribe("y es mayor o igual que x");
    };
    mientras (x < 50) haz {
        holi = 3;
        x = x + 5;
        escribe("x ahora es: ", x);
    };
    miFuncion(x, y);
}fin
```

### Proceso de Compilación:

1. **Declaración de Variables Globales:**
    - `x`, `y`: entero
    - `z`: flotante
    - `holi`: entero
2. **Declaración de la Función `miFuncion`**
    - Parámetros: `c` (entero), `a` (entero)
    - Variable Local: `pi` (flotante)
    - Instrucciones:
      - `pi = 3.14`
      - `c = a + 10`
      - `escribe("El valor de c es: ", c)`
3. **Código Principal:**
    - `x = 10`
    - `y = 20`
    - `z = x + y * 1.5`
    - Condicional `si (x > y) { ... } sino { ... }`
    - Ciclo `mientras (x < 50) haz { ... }`
    - Llamada a la función `miFuncion(x, y)`

### Generación de Cuádruplos:

Los cuádruplos representan las operaciones y el flujo del programa en una forma intermedia.

Ejemplo de algunos cuádruplos generados:

- Asignación de `x` y `y`:
  ```makefile
    (6): (=, 10, None, x)
    (7): (=, 20, None, y)
  ```
- Cálculo de `z`:
  ```makefile
    (8): (*, y, 1.5, t1)
    (9): (+, x, t1, t2)
    (10): (=, t2, None, z)
  ```
- Condicional `si (x > y)`:
  ```makefile
    (11): (>, x, y, t3)
    (12): (GOTOF, t3, None, 15)
    (13): (PRINT, "x es mayor que y", None, None)
    (14): (GOTO, None, None, 16)
    (15): (PRINT, "y es mayor o igual que x", None, None)
  ```
- Ciclo `mientras (x < 50) haz`:
  ```makefile
    (16): (<, x, 50, t4)
    (17): (GOTOF, t4, None, 24)
    (18): (=, 3, None, holi)
    (19): (+, x, 5, t5)
    (20): (=, t5, None, x)
    (21): (PRINT, "x ahora es: ", None, None)
    (22): (PRINT, x, None, None)
    (23): (GOTO, None, None, 16)
  ```
- Llamada a la función `miFuncion(x, y)`:
  ```makefile
    (24): (PARAM, x, None, param0)
    (25): (PARAM, y, None, param1)
    (26): (GOSUB, miFuncion, None, 0)
  ```

**Explicación de Cuádruplos de la Función `miFuncion`:**
- Inicio en el cuádruplo `(0)`.
- Asignaciones y operaciones dentro de la función.
- Cuádruplo `(5)` marca el fin de la función con `(ENDFUNC, None, None, None)`.