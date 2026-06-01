import os
import pickle
from typing import Dict, Optional, List

from modelo import PacientePediatrico

class RepositorioPacientes:
    """
    Clase encargada de gestionar los pacientes registrados en el sistema. Incluye CRUD para los pacientes además de la persistencia para no perder los datos.
    Implementa el patrón Singleton para garantizar una única instancia de la clase en toda la aplicación.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Implementación del patrón Singleton para garantizar una única instancia.
        Intercepta la creación del objeto para devolver siempre la misma instancia.
        """
        if cls._instance is None:
            cls._instance = super(RepositorioPacientes, cls).__new__(cls)
            cls._instance._inicializado = False
        return cls._instance
    
    def __init__(self):
        """
        Inicializador de la clase 'RepositorioPacientes' 
        """
        if not self._inicializado:
            self._archivo_destino: str = "datos/pacientes.pkl"
            self._pacientes: Dict[str, PacientePediatrico] = {}
            self._inicializado = True
    
    def crear(self, paciente: PacientePediatrico) -> bool:
        """
        Método para insertar un nuevo paciente en el repositorio.
        Recibe un objeto PacientePediatrico como parámetro.
        Retorna un true en caso de éxito, retorna un false en caso contrario.
        """
        try:
            if not isinstance(paciente, PacientePediatrico):
                raise TypeError("El objeto no es una instancia de tipo 'PacientePediatrico'")
            
            if paciente.curp in self._pacientes:
                print(f"El paciente con curp '{paciente.curp}' ya existe en el repositorio.")
                return False
            
            self._pacientes[paciente.curp] = paciente
            return True
        except Exception as e:
            print(f'Error al crear paciente: {e}')
            return False
    
    def leer(self, curp: str)-> Optional[PacientePediatrico]:
        """
        Método que busca un paciente por su curp en el repositorio y lo retorna.
        Retrona None si el paciente no existe.
        """
        try:
            return self._pacientes.get(curp.strip().upper())
        except Exception as e:
            print(f'Error al leer paciente: {e}')
            return None

    def leer_todos(self) -> List[PacientePediatrico]:
        """
        Método que devuelve una lista de todos los pacientes registrados en el repositorio.
        """
        try:
            return list(self._pacientes.values())
        except Exception as e:
            print(f'Error al leer todos los pacientes: {e}')
            return []
    
    def actualizar(self, paciente: PacientePediatrico) -> bool:
        """
        Método que actualiza los datos de un paciente en el repositorio.
        Recibe un objeto PacientePediatrico como parámetro.
        Retorna un true en caso de éxito, retorna un false en caso contrario.
        """

        try:
            if not isinstance(paciente, PacientePediatrico):
                raise TypeError("El objeto no es una instancia de tipo 'PacientePediatrico'")
            
            if paciente.curp not in self._pacientes:
                print(f"El paciente con curp '{paciente.curp}' no existe en el repositorio.")
                return False
            
            self._pacientes[paciente.curp] = paciente
            return True
        except Exception as e:
            print(f'Error al actualizar paciente: {e}')
            return False

    def eliminar(self, curp: str) -> bool:
        """
        Método que elimina un paciente del repositorio.
        Recibe un curp como parámetro.
        Retorna un true en caso de éxito, retorna un false en caso contrario.
        """
        try:
            if curp.strip().upper() in self._pacientes:
                del self._pacientes[curp.strip().upper()]
                return True
            else:
                print(f"El paciente con curp '{curp}' no existe en el repositorio.")
                return False
        except Exception as e:
            print(f'Error al eliminar paciente: {e}')
            return False
    
    def guardar_estado(self, ruta_archivo: Optional[str] = None) -> bool:
        """
        Método que guarda los datos del repositorio en un archivo para mantener la persistencia de estos por medio de pickle y with.
        Recibe como parámetro la ruta completa del archivo (ubicación y nombre).
        Retorna un true en caso de éxito, retorna un false en caso contrario.
        """
        ruta = ruta_archivo if ruta_archivo else self._archivo_destino

        try:
            dir = os.path.dirname(ruta)
            if dir and not os.path.exists(dir): 
                os.makedirs(dir, exist_ok=True)

            with open(ruta, 'wb') as archivo:
                pickle.dump(self._pacientes, archivo)
            return True
        except (IOError, pickle.PickleError) as e:
            print(f'Error al guardar archivo: {e}')
            return False
    
    def cargar_estado(self, ruta_archivo: Optional[str] = None) -> bool:
        """
        Método que carga los datos del repositorio desde un archivo ya existente.
        Recibe como parámetro la ruta completa del archivo (ubicación y nombre).
        Retorna un true en caso de éxito, retorna un false en caso contrario.
        """
        ruta = ruta_archivo if ruta_archivo else self._archivo_destino
        try:
            if os.path.exists(ruta):
                with open(ruta, 'rb') as archivo:
                    datos = pickle.load(archivo)
                    if isinstance(datos, dict):
                        for paciente in datos.values():
                            if not hasattr(paciente, 'historial_consultas'):
                                paciente.historial_consultas = []
                        self._pacientes = datos
                        return True
            return False
        except (pickle.PickleError, EOFError) as e:
            print(f'Error al cargar archivo: {e}')
            return False


