"""
Punto de entrada principal del programa.
Este módulo es quien arranca el sistema.
"""
from app import App

def main():
    """
    Función principal del programa.
    """
    try:
        app = App()
        app.iniciar()
    except Exception as e:
        print(f'Error al iniciar aplicación: {e}')

if __name__ == '__main__':
    main()