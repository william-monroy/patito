from PatitoListener import PatitoListener
from PatitoParser import PatitoParser
from VirtualMemory import VirtualMemory

class PatitoCustomListener(PatitoListener):
    def __init__(self):
        # Inicializar el directorio de funciones y tablas de variables
        self.directorio_funciones = {}
        self.tabla_variables_global = {}
        self.tabla_variables_actual = self.tabla_variables_global
        self.funcion_actual = 'global'
        self.errores = []
        # Crear instancia de VirtualMemory
        self.virtual_memory = VirtualMemory()
        # Tabla de constantes
        self.constant_table = {}
        # Pila para manejar scopes
        self.pila_scopes = ['global']
        # Inicializar el cubo semántico
        self.cubo_semantico = self.inicializar_cubo_semantico()
        # Inicializar pilas para operandos, operadores y tipos
        self.pila_operandos = []
        self.pila_operadores = []
        self.pila_tipos = []
        # Inicializar contador de temporales
        self.contador_temporales = 0
        # Lista para almacenar los cuádruplos
        self.cuadruplos = []
        # Pila para manejar saltos
        self.pila_saltos = []
        self.in_condition = False
        # Listas para manejar parámetros en impresión y llamadas
        self.lista_param_impresion = []
        self.pila_parametros = []

    # Entrar a la regla de programa
    def enterPrograma(self, ctx: PatitoParser.ProgramaContext):
        # Iniciar el directorio de funciones con el scope global
        self.directorio_funciones['global'] = {
            'tipo_retorno': 'nula',
            'parametros': [],
            'tabla_variables': self.tabla_variables_global,
            'cuadruplos_inicio': None  # Se asignará durante la generación de código
        }

    def exitPrograma(self, ctx: PatitoParser.ProgramaContext):
        # Agregar el cuádruplo END al final del programa
        cuadruplo = ('END', None, None, None)
        self.cuadruplos.append(cuadruplo)

    # Entrar a la declaración de variables
    def enterD(self, ctx: PatitoParser.DContext):
        scope_actual = self.pila_scopes[-1]
        variables = ctx.ID()
        tipo = ctx.tipo().getText()

        for var in variables:
            nombre_var = var.getText()
            if nombre_var in self.tabla_variables_actual:
                self.errores.append(
                    f"Error: Variable '{nombre_var}' ya declarada en el alcance '{scope_actual}'.")
            else:
                # Asignar dirección virtual
                if scope_actual == 'global':
                    address = self.virtual_memory.get_address('global', tipo)
                else:
                    address = self.virtual_memory.get_address('local', tipo)
                # Agregar la variable a la tabla de variables actual con su dirección
                self.tabla_variables_actual[nombre_var] = {'tipo': tipo, 'direccion': address}

    # Entrar a la declaración de una función
    def enterFuncs(self, ctx: PatitoParser.FuncsContext):
        nombre_funcion = ctx.ID().getText()
        tipo_retorno = ctx.getChild(0).getText()  # 'nula' o tipo de retorno

        if nombre_funcion in self.directorio_funciones:
            self.errores.append(f"Error: Función '{nombre_funcion}' ya declarada.")
        else:
            # Manejar parámetros
            parametros = []
            if ctx.param():
                param_list = ctx.param().getText().split(',')
                for param_pair in param_list:
                    if ':' in param_pair:
                        nombre_param, tipo_param = param_pair.strip().split(':')
                        nombre_param = nombre_param.strip()
                        tipo_param = tipo_param.strip()
                        parametros.append({'nombre': nombre_param, 'tipo': tipo_param})
                    else:
                        continue  # Manejar caso de parámetros vacíos

            # Crear una nueva tabla de variables para la función
            self.tabla_variables_actual = {}
            # Agregar parámetros a la tabla de variables de la función
            for param in parametros:
                nombre_param = param['nombre']
                tipo_param = param['tipo']
                if nombre_param in self.tabla_variables_actual:
                    self.errores.append(
                        f"Error: Parámetro '{nombre_param}' duplicado en función '{nombre_funcion}'.")
                else:
                    # Asignar dirección virtual al parámetro
                    address = self.virtual_memory.get_address('local', tipo_param)
                    self.tabla_variables_actual[nombre_param] = {'tipo': tipo_param, 'direccion': address}

            # Agregar la función al directorio de funciones
            self.directorio_funciones[nombre_funcion] = {
                'tipo_retorno': tipo_retorno,
                'parametros': parametros,
                'tabla_variables': self.tabla_variables_actual,
                'cuadruplos_inicio': len(self.cuadruplos)  # Cuádruplo de inicio de la función
            }
            # Actualizar el scope actual
            self.pila_scopes.append(nombre_funcion)
            self.funcion_actual = nombre_funcion

    # Salir de la declaración de una función
    def exitFuncs(self, ctx: PatitoParser.FuncsContext):
        # Restaurar el scope anterior
        self.pila_scopes.pop()
        self.funcion_actual = self.pila_scopes[-1]
        if self.funcion_actual == 'global':
            self.tabla_variables_actual = self.tabla_variables_global
        else:
            self.tabla_variables_actual = self.directorio_funciones[self.funcion_actual]['tabla_variables']
        # Agregar un cuádruplo de retorno al final de la función
        cuadruplo = ('ENDFUNC', None, None, None)
        self.cuadruplos.append(cuadruplo)
        # Reiniciar la memoria local
        self.virtual_memory.reset_local_memory()

    # Entrar a una asignación
    def enterAsigna(self, ctx: PatitoParser.AsignaContext):
        scope_actual = self.pila_scopes[-1]
        nombre_var = ctx.ID().getText()
        # Verificar si la variable está declarada en el scope actual o global
        if nombre_var not in self.tabla_variables_actual and nombre_var not in self.tabla_variables_global:
            self.errores.append(
                f"Error: Variable '{nombre_var}' no declarada en el alcance '{scope_actual}'.")

    # Entrar a una llamada de función
    def enterLlamada(self, ctx: PatitoParser.LlamadaContext):
        nombre_funcion = ctx.ID().getText()
        # Verificar si la función está declarada
        if nombre_funcion not in self.directorio_funciones:
            self.errores.append(f"Error: Función '{nombre_funcion}' no declarada.")
        else:
            self.pila_parametros = []

    def exitLlamada(self, ctx: PatitoParser.LlamadaContext):
        nombre_funcion = ctx.ID().getText()
        funcion_info = self.directorio_funciones[nombre_funcion]
        num_params = len(funcion_info['parametros'])
        if len(self.pila_parametros) != num_params:
            self.errores.append(f"Error: Número incorrecto de parámetros al llamar a '{nombre_funcion}'.")
        else:
            # Verificar tipos de parámetros y generar cuádruplos
            for i, (param, tipo_param) in enumerate(self.pila_parametros):
                expected_tipo = funcion_info['parametros'][i]['tipo']
                if tipo_param != expected_tipo:
                    self.errores.append(
                        f"Error: Tipo incorrecto para el parámetro {i + 1} al llamar a '{nombre_funcion}'. Se esperaba '{expected_tipo}' pero se obtuvo '{tipo_param}'.")
                cuadruplo = ('PARAM', param, None, f'param{i}')
                self.cuadruplos.append(cuadruplo)
            # Generar cuádruplo de llamada
            cuadruplo = ('GOSUB', nombre_funcion, None, funcion_info['cuadruplos_inicio'])
            self.cuadruplos.append(cuadruplo)

    def exitE_l(self, ctx: PatitoParser.E_lContext):
        expresiones = ctx.expresion()
        if expresiones:
            for _ in expresiones:
                resultado = self.pila_operandos.pop()
                tipo = self.pila_tipos.pop()
                self.pila_parametros.insert(0, (resultado, tipo))

    # Entrar a una variable usada (por ejemplo, en expresiones)
    def enterFactor(self, ctx: PatitoParser.FactorContext):
        if ctx.ID():
            nombre_var = ctx.ID().getText()
            scope_actual = self.pila_scopes[-1]
            # Verificar si la variable está declarada en el scope actual o global
            if nombre_var not in self.tabla_variables_actual and nombre_var not in self.tabla_variables_global:
                self.errores.append(
                    f"Error: Variable '{nombre_var}' no declarada en el alcance '{scope_actual}'.")

    def exitFactor(self, ctx: PatitoParser.FactorContext):
        if ctx.NUMERO():
            valor = ctx.NUMERO().getText()
            if '.' in valor:
                tipo = 'flotante'
            else:
                tipo = 'entero'
            address = self.get_constant_address(valor, tipo)
            self.pila_operandos.append(address)
            self.pila_tipos.append(tipo)
        elif ctx.ID():
            nombre_var = ctx.ID().getText()
            tipo, address = self.obtener_tipo_direccion_variable(nombre_var)
            if tipo:
                self.pila_operandos.append(address)
                self.pila_tipos.append(tipo)
            else:
                self.errores.append(f"Error: Variable '{nombre_var}' no declarada.")
        elif ctx.expresion():
            # Ya se manejó la expresión interna
            pass

    def enterOp(self, ctx: PatitoParser.OpContext):
        operador = ctx.getText()
        self.pila_operadores.append(operador)

    def enterOf(self, ctx: PatitoParser.OfContext):
        operador = ctx.getText()
        self.pila_operadores.append(operador)

    def enterBo(self, ctx: PatitoParser.BoContext):
        operador = ctx.getText()
        self.pila_operadores.append(operador)

    def exitTermino(self, ctx: PatitoParser.TerminoContext):
        while self.pila_operadores and self.pila_operadores[-1] in ['*', '/']:
            operador = self.pila_operadores.pop()
            derecha = self.pila_operandos.pop()
            tipo_derecha = self.pila_tipos.pop()
            izquierda = self.pila_operandos.pop()
            tipo_izquierda = self.pila_tipos.pop()
            resultado_tipo = self.cubo_semantico[tipo_izquierda][operador][tipo_derecha]
            if resultado_tipo:
                # Asignar dirección virtual al temporal
                temporal_address = self.virtual_memory.get_address('temporal', resultado_tipo)
                self.pila_operandos.append(temporal_address)
                self.pila_tipos.append(resultado_tipo)
                cuadruplo = (operador, izquierda, derecha, temporal_address)
                self.cuadruplos.append(cuadruplo)
            else:
                self.errores.append(
                    f"Error semántico: Operación inválida entre '{tipo_izquierda}' y '{tipo_derecha}' con operador '{operador}'.")

    def exitExp(self, ctx: PatitoParser.ExpContext):
        while self.pila_operadores and self.pila_operadores[-1] in ['+', '-']:
            operador = self.pila_operadores.pop()
            derecha = self.pila_operandos.pop()
            tipo_derecha = self.pila_tipos.pop()
            izquierda = self.pila_operandos.pop()
            tipo_izquierda = self.pila_tipos.pop()
            resultado_tipo = self.cubo_semantico[tipo_izquierda][operador][tipo_derecha]
            if resultado_tipo:
                # Asignar dirección virtual al temporal
                temporal_address = self.virtual_memory.get_address('temporal', resultado_tipo)
                self.pila_operandos.append(temporal_address)
                self.pila_tipos.append(resultado_tipo)
                cuadruplo = (operador, izquierda, derecha, temporal_address)
                self.cuadruplos.append(cuadruplo)
            else:
                self.errores.append(
                    f"Error semántico: Operación inválida entre '{tipo_izquierda}' y '{tipo_derecha}' con operador '{operador}'.")

    # Métodos para manejar condicionales
    def exitExpresion(self, ctx: PatitoParser.ExpresionContext):
        # Manejar expresiones relacionales
        if ctx.bo():
            operador = self.pila_operadores.pop()
            derecha = self.pila_operandos.pop()
            tipo_derecha = self.pila_tipos.pop()
            izquierda = self.pila_operandos.pop()
            tipo_izquierda = self.pila_tipos.pop()
            resultado_tipo = self.cubo_semantico[tipo_izquierda][operador][tipo_derecha]
            if resultado_tipo:
                # Asignar dirección virtual al temporal
                temporal_address = self.virtual_memory.get_address('temporal', resultado_tipo)
                self.pila_operandos.append(temporal_address)
                self.pila_tipos.append(resultado_tipo)
                cuadruplo = (operador, izquierda, derecha, temporal_address)
                self.cuadruplos.append(cuadruplo)
            else:
                self.errores.append(
                    f"Error semántico: Operación inválida entre '{tipo_izquierda}' y '{tipo_derecha}' con operador '{operador}'.")

        # Verificar si la expresión es parte de una condición o ciclo
        if self.es_expresion_de_condicion(ctx):
            resultado = self.pila_operandos.pop()
            tipo_resultado = self.pila_tipos.pop()
            if tipo_resultado != 'booleano':
                self.errores.append("Error: La expresión en la condición debe ser booleana.")
            else:
                cuadruplo = ('GOTOF', resultado, None, None)
                self.cuadruplos.append(cuadruplo)
                self.pila_saltos.append(len(self.cuadruplos) - 1)
        elif self.es_expresion_de_ciclo(ctx):
            resultado = self.pila_operandos.pop()
            tipo_resultado = self.pila_tipos.pop()
            if tipo_resultado != 'booleano':
                self.errores.append("Error: La expresión en el ciclo debe ser booleana.")
            else:
                cuadruplo = ('GOTOF', resultado, None, None)
                self.cuadruplos.append(cuadruplo)
                self.pila_saltos.append(len(self.cuadruplos) - 1)

        # Debugging statements
        # print(f"Current pila_operandos: {self.pila_operandos}")
        # print(f"Current pila_tipos: {self.pila_tipos}")
        # print(f"Current pila_operadores: {self.pila_operadores}")
        # print(f"Current pila_saltos: {self.pila_saltos}")
        # print(f"Current cuadruplos: {self.cuadruplos}")

    def exitAsigna(self, ctx: PatitoParser.AsignaContext):
        variable = ctx.ID().getText()
        valor = self.pila_operandos.pop()
        tipo_valor = self.pila_tipos.pop()
        tipo_variable, address_variable = self.obtener_tipo_direccion_variable(variable)
        if tipo_variable:
            # Verificar compatibilidad de tipos
            resultado_tipo = self.cubo_semantico[tipo_variable]['='][tipo_valor]
            if resultado_tipo:
                cuadruplo = ('=', valor, None, address_variable)
                self.cuadruplos.append(cuadruplo)
            else:
                self.errores.append(
                    f"Error semántico: No se puede asignar un valor de tipo '{tipo_valor}' a la variable '{variable}' de tipo '{tipo_variable}'.")
        else:
            self.errores.append(f"Error: Variable '{variable}' no declarada.")

    # Métodos para manejar condicionales
    def enterCondicion(self, ctx: PatitoParser.CondicionContext):
        print("Entering a condition")

    def exitCondicion(self, ctx: PatitoParser.CondicionContext):
        if self.pila_saltos:
            end = self.pila_saltos.pop()
            self.cuadruplos[end] = (self.cuadruplos[end][0], self.cuadruplos[end][1], None, len(self.cuadruplos))
        else:
            self.errores.append("Error: pila_saltos está vacía en exitCondicion.")

    def enterE_c(self, ctx: PatitoParser.E_cContext):
        # Generar el cuádruplo GOTO para saltar al final de la condición después del bloque 'sino'
        cuadruplo = ('GOTO', None, None, None)
        self.cuadruplos.append(cuadruplo)
        goto_index = len(self.cuadruplos) - 1

        # Sacar el índice del GOTOF previo y completar su salto al inicio del bloque 'sino'
        falso = self.pila_saltos.pop()
        self.cuadruplos[falso] = (self.cuadruplos[falso][0], self.cuadruplos[falso][1], None, len(self.cuadruplos))

        # Agregar el índice del GOTO a la pila de saltos para completarlo al final del 'sino'
        self.pila_saltos.append(goto_index)

    def exitE_c(self, ctx: PatitoParser.E_cContext):
        # No es necesario hacer nada aquí
        pass

    # Métodos para manejar ciclos
    def enterCiclo(self, ctx: PatitoParser.CicloContext):
        self.pila_saltos.append(len(self.cuadruplos))

    def exitCiclo(self, ctx: PatitoParser.CicloContext):
        falso = self.pila_saltos.pop()
        retorno = self.pila_saltos.pop()
        cuadruplo = ('GOTO', None, None, retorno)
        self.cuadruplos.append(cuadruplo)
        self.cuadruplos[falso] = (self.cuadruplos[falso][0], self.cuadruplos[falso][1], None, len(self.cuadruplos))

    # Métodos para manejar impresión
    def enterImprime(self, ctx: PatitoParser.ImprimeContext):
        self.lista_param_impresion = []

    def exitImprime(self, ctx: PatitoParser.ImprimeContext):
        # Generar cuádruplos PRINT en orden
        for parametro in self.lista_param_impresion:
            cuadruplo = ('PRINT', parametro, None, None)
            self.cuadruplos.append(cuadruplo)
        # Limpiar la lista
        self.lista_param_impresion = []

    def exitParam_imp(self, ctx: PatitoParser.Param_impContext):
        if ctx.expresion():
            resultado = self.pila_operandos.pop()
            tipo = self.pila_tipos.pop()
            self.lista_param_impresion.insert(0, resultado)  # Insertar al inicio para mantener el orden
        elif ctx.LETRERO():
            valor = ctx.LETRERO().getText()
            tipo = 'cadena'
            address = self.get_constant_address(valor, tipo)
            self.lista_param_impresion.insert(0, address)

    def obtener_tipo_variable(self, nombre_var):
        if nombre_var in self.tabla_variables_actual:
            return self.tabla_variables_actual[nombre_var]['tipo']
        elif nombre_var in self.tabla_variables_global:
            return self.tabla_variables_global[nombre_var]['tipo']
        else:
            return None

    def obtener_tipo_direccion_variable(self, nombre_var):
        if nombre_var in self.tabla_variables_actual:
            var_info = self.tabla_variables_actual[nombre_var]
            print(
                f"Variable '{nombre_var}' encontrada en ámbito actual: Tipo={var_info['tipo']}, Dirección={var_info['direccion']}")
            return var_info['tipo'], var_info['direccion']
        elif nombre_var in self.tabla_variables_global:
            var_info = self.tabla_variables_global[nombre_var]
            print(
                f"Variable '{nombre_var}' encontrada en ámbito global: Tipo={var_info['tipo']}, Dirección={var_info['direccion']}")
            return var_info['tipo'], var_info['direccion']
        else:
            print(f"Variable '{nombre_var}' no declarada.")
            return None, None

    def inicializar_cubo_semantico(self):
        tipos = ['entero', 'flotante']
        operadores = ['+', '-', '*', '/', '>', '<', '>=', '<=', '==', '!=', '=']
        cubo = {}

        for tipo1 in tipos:
            cubo[tipo1] = {}
            for operador in operadores:
                cubo[tipo1][operador] = {}
                for tipo2 in tipos:
                    resultado = None  # Por defecto, la operación no es válida
                    if operador in ['+', '-', '*', '/']:
                        # Reglas para operadores aritméticos
                        if tipo1 == 'entero' and tipo2 == 'entero':
                            resultado = 'entero'
                        elif tipo1 in ['entero', 'flotante'] and tipo2 in ['entero', 'flotante']:
                            resultado = 'flotante'
                    elif operador in ['>', '<', '>=', '<=', '==', '!=']:
                        # Reglas para operadores relacionales
                        if tipo1 in ['entero', 'flotante'] and tipo2 in ['entero', 'flotante']:
                            resultado = 'booleano'
                    elif operador == '=':
                        # Reglas para asignación
                        if tipo1 == tipo2:
                            resultado = tipo1
                    cubo[tipo1][operador][tipo2] = resultado
        return cubo

    def es_expresion_de_condicion(self, ctx):
        parent_ctx = ctx.parentCtx
        while parent_ctx:
            if isinstance(parent_ctx, PatitoParser.CondicionContext) and ctx == parent_ctx.expresion():
                return True
            parent_ctx = parent_ctx.parentCtx
        return False

    def es_expresion_de_ciclo(self, ctx):
        parent_ctx = ctx.parentCtx
        while parent_ctx:
            if isinstance(parent_ctx, PatitoParser.CicloContext) and ctx == parent_ctx.expresion():
                return True
            parent_ctx = parent_ctx.parentCtx
        return False

    def get_constant_address(self, valor, tipo):
        if valor not in self.constant_table:
            address = self.virtual_memory.get_address('constante', tipo)
            self.constant_table[valor] = {'tipo': tipo, 'direccion': address}
        else:
            address = self.constant_table[valor]['direccion']
        return address