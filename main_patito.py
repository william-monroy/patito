import sys
from antlr4 import *
from PatitoLexer import PatitoLexer
from PatitoParser import PatitoParser
from PatitoVisitor import PatitoVisitor  # Asegúrate de que esto esté presente

class EvalVisitor(PatitoVisitor):
    """
    Visitor personalizado para el análisis semántico y la interpretación del código.
    """
    def visitPrograma(self, ctx):
        return [self.visit(s) for s in ctx.cuerpo()]

    def visitAsigna(self, ctx):
        # Implementar la lógica para la asignación.
        variable = ctx.ID().getText()
        value = self.visit(ctx.expresion())
        print(f"Asigna: {variable} = {value}")
        return value

    def visitImprime(self, ctx):
        if ctx.param_imp():
            print(ctx.param_imp().getText())

    # Añadir más métodos visit para los diferentes tipos de nodos según la gramática

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
    except Exception as e:
        print(f"Error durante el análisis léxico/sintáctico: {e}")
        sys.exit(1)

    # Evaluación del árbol sintáctico
    try:
        visitor = EvalVisitor()
        resultado = visitor.visit(tree)
        print("Resultado:", resultado)
    except Exception as e:
        print(f"Error durante la evaluación del árbol sintáctico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)
