from PatitoListener import PatitoListener
from PatitoParser import PatitoParser

class PatitoCustomListener(PatitoListener):
    def __init__(self):
        # Inicializar el directorio de funciones y tablas de variables
        self.directorio_funciones = {}
        self.tabla_variables_global = {}
        self.tabla_variables_actual = self.tabla_variables_global
        self.funcion_actual = 'global'
        self.errores = []
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

    # Entrar a la regla de programa
    def enterPrograma(self, ctx: PatitoParser.ProgramaContext):
        # Iniciar el directorio de funciones con el scope global
        self.directorio_funciones['global'] = {
            'tipo_retorno': 'nula',
            'parametros': [],
            'tabla_variables': self.tabla_variables_global,
            'cuadruplos_inicio': None  # Se asignará durante la generación de código
        }

    # Entrar a la declaración de variables
    def enterD(self, ctx: PatitoParser.DContext):
        scope_actual = self.pila_scopes[-1]
        variables = ctx.ID()
        tipo = ctx.tipo().getText()

        for var in variables:
            nombre_var = var.getText()
            # Verificar si la variable ya ha sido declarada en el scope actual
            if nombre_var in self.tabla_variables_actual:
                self.errores.append(
                    f"Error: Variable '{nombre_var}' ya declarada en el alcance '{scope_actual}'.")
            else:
                # Agregar la variable a la tabla de variables actual
                self.tabla_variables_actual[nombre_var] = {'tipo': tipo}

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
                    self.tabla_variables_actual[nombre_param] = {'tipo': tipo_param}

            # Agregar la función al directorio de funciones
            self.directorio_funciones[nombre_funcion] = {
                'tipo_retorno': tipo_retorno,
                'parametros': parametros,
                'tabla_variables': self.tabla_variables_actual,
                'cuadruplos_inicio': None  # Se asignará durante la generación de código
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
            self.pila_operandos.append(valor)
            self.pila_tipos.append(tipo)
        elif ctx.ID():
            nombre_var = ctx.ID().getText()
            tipo = self.obtener_tipo_variable(nombre_var)
            if tipo:
                self.pila_operandos.append(nombre_var)
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
                temporal = f"t{self.contador_temporales}"
                self.contador_temporales += 1
                self.pila_operandos.append(temporal)
                self.pila_tipos.append(resultado_tipo)
                cuadruplo = (operador, izquierda, derecha, temporal)
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
                temporal = f"t{self.contador_temporales}"
                self.contador_temporales += 1
                self.pila_operandos.append(temporal)
                self.pila_tipos.append(resultado_tipo)
                cuadruplo = (operador, izquierda, derecha, temporal)
                self.cuadruplos.append(cuadruplo)
            else:
                self.errores.append(
                    f"Error semántico: Operación inválida entre '{tipo_izquierda}' y '{tipo_derecha}' con operador '{operador}'.")

    def exitExpresion(self, ctx: PatitoParser.ExpresionContext):
        if ctx.bo():
            operador = self.pila_operadores.pop()
            derecha = self.pila_operandos.pop()
            tipo_derecha = self.pila_tipos.pop()
            izquierda = self.pila_operandos.pop()
            tipo_izquierda = self.pila_tipos.pop()
            resultado_tipo = self.cubo_semantico[tipo_izquierda][operador][tipo_derecha]
            if resultado_tipo:
                temporal = f"t{self.contador_temporales}"
                self.contador_temporales += 1
                self.pila_operandos.append(temporal)
                self.pila_tipos.append(resultado_tipo)
                cuadruplo = (operador, izquierda, derecha, temporal)
                self.cuadruplos.append(cuadruplo)
            else:
                self.errores.append(
                    f"Error semántico: Operación inválida entre '{tipo_izquierda}' y '{tipo_derecha}' con operador '{operador}'.")

    def exitAsigna(self, ctx: PatitoParser.AsignaContext):
        variable = ctx.ID().getText()
        valor = self.pila_operandos.pop()
        tipo_valor = self.pila_tipos.pop()
        tipo_variable = self.obtener_tipo_variable(variable)
        if tipo_variable:
            # Verificar compatibilidad de tipos
            resultado_tipo = self.cubo_semantico[tipo_variable]['='][tipo_valor]
            if resultado_tipo:
                cuadruplo = ('=', valor, None, variable)
                self.cuadruplos.append(cuadruplo)
            else:
                self.errores.append(
                    f"Error semántico: No se puede asignar un valor de tipo '{tipo_valor}' a la variable '{variable}' de tipo '{tipo_variable}'.")
        else:
            self.errores.append(f"Error: Variable '{variable}' no declarada.")

    def obtener_tipo_variable(self, nombre_var):
        if nombre_var in self.tabla_variables_actual:
            return self.tabla_variables_actual[nombre_var]['tipo']
        elif nombre_var in self.tabla_variables_global:
            return self.tabla_variables_global[nombre_var]['tipo']
        else:
            return None

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

