import os
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()

test_folder = "test_cases"
os.makedirs(test_folder, exist_ok=True)

# Lista de casos de prueba con títulos actualizados y en orden
test_cases = [
    {
        'name': 'test1',
        'description': 'Prueba Básica de Declaración y Asignación',
        'code': '''
vars
    a: entero;
    b: flotante;

inicio{
    a = 10;
    b = 20.5;
    escribe("Valor de a:", a);
    escribe("Valor de b:", b);
}fin
''',
        'expect_error': False
    },
    {
        'name': 'test2',
        'description': 'Operaciones Aritméticas Básicas',
        'code': '''
vars
    x: flotante;
    y: flotante;
    z: flotante;
inicio{
    x = 15.0;
    y = 4.2;
    z = x + y * 2 - (x / y);
    escribe("El resultado de z es:", z);
}fin
''',
        'expect_error': False
    },
    {
        'name': 'test3',
        'description': 'Condicional Simple',
        'code': '''
vars
    num: entero;
inicio{
    num = 5;
    si (num > 0) {
        escribe("El número es positivo.");
    } sino {
        escribe("El número es negativo o cero.");
    };
}fin
''',
        'expect_error': False
    },
    {
        'name': 'test4',
        'description': 'Ciclo mientras',
        'code': '''
vars
    contador: entero;
inicio{
    contador = 1;
    mientras (contador <= 5) haz {
        escribe("Contador:", contador);
        contador = contador + 1;
    };
}fin
''',
        'expect_error': False
    },
    {
        'name': 'test5',
        'description': 'Manejo de Errores: Variable No Declarada',
        'code': '''
vars
    x: entero;

inicio{
    x = 10;
    y = x + 5;  // 'y' no está declarada
    escribe("Valor de y:", y);
}fin
''',
        'expect_error': True
    },
    {
        'name': 'test6',
        'description': 'Manejo de Errores: Tipo Incorrecto en Asignación',
        'code': '''
vars
    a: entero;

inicio{
    a = 3.14;  // Asignando flotante a entero
    escribe("Valor de a:", a);
}fin
''',
        'expect_error': True
    },
    {
        'name': 'test7',
        'description': 'Funciones Sin Parámetros y Sin Retorno',
        'code': '''
nula saludo() {
    {
        escribe("¡Hola, mundo!");
    }
};

inicio{
    saludo();
}fin
''',
        'expect_error': False
    },
    {
        'name': 'test8',
        'description': 'Operaciones con Flotantes y Conversión Implícita',
        'code': '''
vars
    a: flotante;
    b: entero;
    c: flotante;
inicio{
    a = 5.5;
    b = 2;
    c = a / b;
    escribe("El resultado de c es:", c);
}fin
''',
        'expect_error': False
    },
    {
        'name': 'test9',
        'description': 'Prueba de División por Cero',
        'code': '''
vars
    num: entero;
    denom: entero;
    resultado: entero;
inicio{
    num = 10;
    denom = 0;
    resultado = num / denom;
    escribe("El resultado es:", resultado);
}fin
''',
        'expect_error': False
        # La división por cero es un error en tiempo de ejecución, el compilador puede no detectarlo
    },
]


def display_test_result(test_name, description, result, stdout, stderr, expect_error):
    if result.returncode == 0 and not expect_error:
        console.print(f":white_check_mark: [bold green]{test_name}[/] - {description} PASSED", style="bold green")
        console.print(Panel(stdout, title="Output", expand=False, border_style="green"))
    elif result.returncode != 0 and expect_error:
        console.print(f":white_check_mark: [bold green]{test_name}[/] - {description} PASSED (Expected Error)",
                      style="bold green")
        console.print(Panel(stderr, title="Expected Error Output", expand=False, border_style="green"))
    else:
        console.print(f":x: [bold red]{test_name}[/] - {description} FAILED", style="bold red")
        if stdout:
            console.print(Panel(stdout, title="Compiler Output", expand=False, border_style="red"))
        if stderr:
            console.print(Panel(stderr, title="Compiler Error Output", expand=False, border_style="red"))


def main():
    compiler_command = 'python main_patito.py'
    total_tests = len(test_cases)
    passed_tests = 0

    console.print(f"\n[bold yellow]Running {total_tests} test cases[/]", style="bold yellow")

    for test in test_cases:
        test_name = test['name']
        description = test['description']

        # Crear archivo .patito en la carpeta de test_cases
        patito_filename = os.path.join(test_folder, f"{test_name}.patito")
        with open(patito_filename, 'w', encoding='utf-8') as f:
            f.write(f"programa {test_name};\n")
            f.write(test['code'])

        # Ejecutar compilador
        try:
            result = subprocess.run(
                f"{compiler_command} {patito_filename}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        except Exception as e:
            console.print(f"[bold red]Error running compiler:[/]", e)
            continue

        # Capturar salida y determinar si pasó el test
        stdout = result.stdout
        stderr = result.stderr

        if (test['expect_error'] and result.returncode != 0) or (not test['expect_error'] and result.returncode == 0):
            passed_tests += 1

        # Mostrar resultado del test
        display_test_result(test_name, description, result, stdout, stderr, test['expect_error'])

    # Resumen de resultados
    summary_text = Text(f"\n{passed_tests} out of {total_tests} tests passed.",
                        style="bold green" if passed_tests == total_tests else "bold red")
    console.print(Panel(summary_text, title="Test Summary", box=box.DOUBLE))


if __name__ == '__main__':
    main()
