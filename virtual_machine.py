import sys
import argparse  # Importamos argparse para manejar argumentos de línea de comandos

class MemoryStack:
    def __init__(self):
        self.stack = []

    def push(self, local_memory, temp_memory):
        self.stack.append((local_memory, temp_memory))

    def pop(self):
        if self.stack:
            return self.stack.pop()
        else:
            raise Exception("Error: Pila de memoria vacía al intentar hacer pop.")

    def current_local(self):
        if self.stack:
            return self.stack[-1][0]
        else:
            return {}

    def current_temp(self):
        if self.stack:
            return self.stack[-1][1]
        else:
            return {}

class Memory:
    def __init__(self):
        # Rango de direcciones virtuales
        self.global_range = (1000, 4999)
        self.local_range = (5000, 8999)
        self.temp_range = (9000, 12999)
        self.const_range = (13000, 16999)

        # Diccionarios para almacenar los valores
        self.global_memory = {}
        self.constant_memory = {}
        self.memory_stack = MemoryStack()

    def get_value(self, address):
        address = int(address)
        if self.global_range[0] <= address <= self.global_range[1]:
            return self.global_memory.get(address, None)
        elif self.local_range[0] <= address <= self.local_range[1]:
            return self.memory_stack.current_local().get(address, None)
        elif self.temp_range[0] <= address <= self.temp_range[1]:
            return self.memory_stack.current_temp().get(address, None)
        elif self.const_range[0] <= address <= self.const_range[1]:
            return self.constant_memory.get(address, None)
        else:
            raise Exception(f"Dirección inválida: {address}")

    def set_value(self, address, value):
        address = int(address)
        if self.global_range[0] <= address <= self.global_range[1]:
            self.global_memory[address] = value
        elif self.local_range[0] <= address <= self.local_range[1]:
            self.memory_stack.current_local()[address] = value
        elif self.temp_range[0] <= address <= self.temp_range[1]:
            self.memory_stack.current_temp()[address] = value
        elif self.const_range[0] <= address <= self.const_range[1]:
            self.constant_memory[address] = value
        else:
            raise Exception(f"Dirección inválida: {address}")

def print_memory(memoria):
    print("Memoria Global:")
    for addr, val in memoria.global_memory.items():
        print(f"  Dirección {addr}: {val}")
    print("Memoria Constante:")
    for addr, val in memoria.constant_memory.items():
        print(f"  Dirección {addr}: {val}")
    print("Memoria Local Actual:")
    for addr, val in memoria.memory_stack.current_local().items():
        print(f"  Dirección {addr}: {val}")
    print("Memoria Temporal Actual:")
    for addr, val in memoria.memory_stack.current_temp().items():
        print(f"  Dirección {addr}: {val}")

def main():
    # Parser para argumentos de línea de comandos
    parser = argparse.ArgumentParser(description='Ejecuta la máquina virtual de Patito.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Activa el modo detallado.')
    args = parser.parse_args()

    # Variable para el modo detallado
    verbose = args.verbose

    # Leer los cuádruplos desde 'output.txt'
    cuadruplos = []
    try:
        with open('output.txt', 'r') as f:
            for line in f:
                operador, operando1, operando2, resultado = line.strip().split(',')
                cuadruplos.append((operador, operando1, operando2, resultado))
    except FileNotFoundError:
        print("Error: 'output.txt' no encontrado.")
        return

    # Leer las constantes desde 'constants.txt'
    constantes = {}
    try:
        with open('constants.txt', 'r') as f:
            for line in f:
                direccion, valor, tipo = line.strip().split(',', 2)
                direccion = int(direccion)
                if tipo == 'entero':
                    valor = int(valor)
                elif tipo == 'flotante':
                    valor = float(valor)
                elif tipo == 'cadena':
                    valor = valor.strip('"')
                else:
                    print(f"Advertencia: Tipo desconocido '{tipo}' para la constante.")
                constantes[direccion] = {'valor': valor, 'tipo': tipo}
    except FileNotFoundError:
        print("Error: 'constants.txt' no encontrado.")
        return

    # Inicializar la memoria
    memoria = Memory()

    # Cargar las constantes en la memoria
    for direccion, info in constantes.items():
        memoria.set_value(direccion, info['valor'])

    # Inicializar el contexto global
    memoria.memory_stack.push({}, {})

    # Pila para manejar los retornos de funciones
    pila_retornos = []

    # Variables para manejar preparación de funciones
    prepared_local_memory = None
    prepared_temp_memory = None

    # Ejecutar los cuádruplos
    contador = 0
    while contador < len(cuadruplos):
        cuadruplo = cuadruplos[contador]
        operador, operando1, operando2, resultado = cuadruplo

        if verbose:
            print(f"\nEjecutando cuádruplo {contador}: ({operador}, {operando1}, {operando2}, {resultado})")

        try:
            if operador == 'GOTO':
                if resultado is None:
                    raise Exception("Error: Cuádruplo GOTO sin dirección de salto.")
                if verbose:
                    print(f"Saltando a cuádruplo {resultado}")
                contador = int(resultado)
                continue
            elif operador == 'MAIN_START':
                contador += 1
                continue
            elif operador == 'GOTOF':
                condicion = memoria.get_value(operando1)
                if verbose:
                    print(f"Evaluando GOTOF, condición en dirección {operando1}: {condicion}")
                if not condicion:
                    if resultado is None:
                        raise Exception("Error: Cuádruplo GOTOF sin dirección de salto.")
                    if verbose:
                        print(f"Condición falsa, saltando a cuádruplo {resultado}")
                    contador = int(resultado)
                    continue
            elif operador == 'ERA':
                if verbose:
                    print(f"Preparando espacio para la función '{operando1}'")
                # Preparar nuevos contextos de memoria local y temporal
                prepared_local_memory = {}
                prepared_temp_memory = {}
            elif operador == 'PARAM':
                valor = memoria.get_value(operando1)
                if verbose:
                    print(f"Asignando parámetro: valor {valor} a dirección {resultado}")
                if valor is None:
                    raise Exception("Error: Operando no inicializado en PARAM.")
                direccion_parametro = int(resultado)
                if prepared_local_memory is not None:
                    prepared_local_memory[direccion_parametro] = valor
                else:
                    raise Exception("Error: No hay contexto de función preparado para PARAM.")
            elif operador == 'GOSUB':
                if verbose:
                    print(f"Llamando a la función '{operando1}' en el cuádruplo {resultado}")
                # Guardar la posición de retorno
                pila_retornos.append(contador + 1)
                # Empujar el contexto de memoria preparado
                if prepared_local_memory is not None and prepared_temp_memory is not None:
                    memoria.memory_stack.push(prepared_local_memory, prepared_temp_memory)
                    # Resetear los contextos preparados
                    prepared_local_memory = None
                    prepared_temp_memory = None
                else:
                    raise Exception("Error: No hay contexto de función preparado para GOSUB.")
                # Saltar al inicio de la función
                direccion_funcion = int(resultado)
                contador = direccion_funcion
                continue
            elif operador == 'ENDFUNC':
                if verbose:
                    print("Finalizando función y regresando al punto de llamada.")
                # Restaurar el contexto anterior
                memoria.memory_stack.pop()
                # Recuperar la posición de retorno
                if not pila_retornos:
                    raise Exception("Error: Pila de retornos vacía al finalizar función.")
                contador = pila_retornos.pop()
                continue
            elif operador in ['+', '-', '*', '/']:
                valor1 = memoria.get_value(operando1)
                valor2 = memoria.get_value(operando2)
                if verbose:
                    print(f"Operando 1: Dirección {operando1} Valor {valor1}")
                    print(f"Operando 2: Dirección {operando2} Valor {valor2}")
                if valor1 is None or valor2 is None:
                    raise Exception(f"Error: Operando(s) no inicializado(s) en operación '{operador}'.")
                if operador == '+':
                    resultado_valor = valor1 + valor2
                elif operador == '-':
                    resultado_valor = valor1 - valor2
                elif operador == '*':
                    resultado_valor = valor1 * valor2
                elif operador == '/':
                    if valor2 == 0:
                        raise Exception("Error: División por cero.")
                    resultado_valor = valor1 / valor2
                if verbose:
                    print(f"Resultado de la operación: {resultado_valor}")
                memoria.set_value(int(resultado), resultado_valor)
            elif operador in ['>', '<', '>=', '<=', '==', '!=']:
                valor1 = memoria.get_value(operando1)
                valor2 = memoria.get_value(operando2)
                if verbose:
                    print(f"Operando 1: Dirección {operando1} Valor {valor1}")
                    print(f"Operando 2: Dirección {operando2} Valor {valor2}")
                if valor1 is None or valor2 is None:
                    raise Exception(f"Error: Operando(s) no inicializado(s) en operación relacional '{operador}'.")
                if operador == '>':
                    resultado_valor = valor1 > valor2
                elif operador == '<':
                    resultado_valor = valor1 < valor2
                elif operador == '>=':
                    resultado_valor = valor1 >= valor2
                elif operador == '<=':
                    resultado_valor = valor1 <= valor2
                elif operador == '==':
                    resultado_valor = valor1 == valor2
                elif operador == '!=':
                    resultado_valor = valor1 != valor2
                if verbose:
                    print(f"Resultado de la operación: {resultado_valor}")
                memoria.set_value(int(resultado), resultado_valor)
            elif operador == '=':
                valor = memoria.get_value(operando1)
                if verbose:
                    print(f"Asignando: Dirección {resultado} Valor {valor}")
                if valor is None:
                    raise Exception(f"Error: Operando no inicializado en asignación '='.")
                memoria.set_value(int(resultado), valor)
            elif operador == 'PRINT':
                valor = memoria.get_value(operando1)
                if valor is None:
                    raise Exception("Error: Operando no inicializado en PRINT.")
                print(valor)
            elif operador == 'END':
                if verbose:
                    print("Fin de la ejecución.")
                break
            else:
                raise Exception(f"Operador desconocido: '{operador}'.")
        except Exception as e:
            print(f"Error en cuádruplo {contador}: {e}")
            break

        if verbose:
            print_memory(memoria)

        contador += 1

if __name__ == '__main__':
    main()
