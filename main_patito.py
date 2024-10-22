import sys
from antlr4 import *
from PatitoLexer import PatitoLexer
from PatitoParser import PatitoParser


def main():
    """
    Función principal para cargar la entrada desde un archivo, tokenizar y analizar sintácticamente el código.
    """
    if len(sys.argv) != 2:
        print("Uso: python main.py <archivo.patito>")
        sys.exit(1)

    archivo_ruta = sys.argv[1]
    if not archivo_ruta.endswith('.patito'):
        print("Error: El archivo debe tener la extensión .patito")
        sys.exit(1)

    try:
        with open(archivo_ruta, 'r') as archivo:
            input_stream = InputStream(archivo.read())
    except FileNotFoundError:
        print(f"Error: el archivo '{archivo_ruta}' no existe.")
        sys.exit(1)
    except IOError as e:
        print(f"Error al leer el archivo '{archivo_ruta}': {e}")
        sys.exit(1)

    try:
        lexer = PatitoLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = PatitoParser(token_stream)
        tree = parser.programa()

        if parser.getNumberOfSyntaxErrors() > 0:
            print("Error: Se encontraron errores de sintaxis en el archivo.")
            sys.exit(1)
        else:
            print("Análisis léxico y sintáctico completado sin errores.")
    except Exception as e:
        print(f"Error durante el análisis léxico/sintáctico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)
