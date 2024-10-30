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

    # Puedes agregar métodos adicionales para otras validaciones y acciones
