import sys
from antlr4 import *
from PatitoLexer import PatitoLexer
from PatitoParser import PatitoParser
from PatitoCustomListener import PatitoCustomListener  # Importamos el Listener personalizado
import traceback

def main():
    """
    Función principal para cargar la entrada desde un archivo, tokenizar y analizar sintácticamente el código.
    """
    if len(sys.argv) != 2:
        print("Uso: python main_patito.py <archivo.patito>")
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
            # Crear instancia del Listener personalizado
            listener = PatitoCustomListener()
            walker = ParseTreeWalker()
            walker.walk(listener, tree)
            # Verificar si hay errores semánticos

            if listener.errores:
                for error in listener.errores:
                    print(error)
                sys.exit(1)
            else:
                print("Análisis semántico completado sin errores.\n")

                # Imprimir el directorio de funciones
                print("==== Directorio de Funciones ====\n")
                for func_name, func_info in listener.directorio_funciones.items():
                    print(f"Función '{func_name}':")
                    print(f"  Tipo de Retorno: {func_info['tipo_retorno']}")
                    if func_info['parametros']:
                        print(f"  Parámetros:")
                        for param in func_info['parametros']:
                            print(f"    - {param['nombre']}: {param['tipo']}")
                    else:
                        print(f"  Parámetros: Ninguno")
                    print(f"  Tabla de Variables:")
                    for var_name, var_info in func_info['tabla_variables'].items():
                        print(f"    - {var_name}: Tipo: {var_info['tipo']}, Dirección: {var_info['direccion']}")
                    print(f"  Cuádruplo de Inicio: {func_info['cuadruplos_inicio']}\n")

                # Imprimir las tablas de variables
                print("==== Tablas de Variables ====\n")
                print("Global:")
                for var_name, var_info in listener.tabla_variables_global.items():
                    print(f"  - {var_name}: Tipo: {var_info['tipo']}, Dirección: {var_info['direccion']}")
                for func_name, func_info in listener.directorio_funciones.items():
                    if func_name != 'global':
                        print(f"\n{func_name}:")
                        for var_name, var_info in func_info['tabla_variables'].items():
                            print(f"  - {var_name}: Tipo: {var_info['tipo']}, Dirección: {var_info['direccion']}")

                # Imprimir la tabla de constantes
                print("\n==== Tabla de Constantes ====\n")
                for const_value, const_info in listener.constant_table.items():
                    print(f"  - {const_value}: Tipo: {const_info['tipo']}, Dirección: {const_info['direccion']}")

                # Imprimir los cuádruplos
                print("\n==== Cuádruplos Generados ====\n")
                for idx, cuadruplo in enumerate(listener.cuadruplos):
                    operador, operando1, operando2, resultado = cuadruplo
                    print(f"{idx}: ({operador}, {operando1}, {operando2}, {resultado})")

                # Escribir los cuádruplos en un archivo
                with open('output.txt', 'w') as f:
                    for idx, cuadruplo in enumerate(listener.cuadruplos):
                        operador, operando1, operando2, resultado = cuadruplo
                        f.write(f"{operador},{operando1},{operando2},{resultado}\n")

                # Escribir la tabla de constantes en un archivo
                with open('constants.txt', 'w') as f:
                    for const_value, const_info in listener.constant_table.items():
                        f.write(f"{const_info['direccion']},{const_value},{const_info['tipo']}\n")



    except Exception as e:
        print(f"Error durante el análisis léxico/sintáctico: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
