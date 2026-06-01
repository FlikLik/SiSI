import csv
import os
import pickle
import statistics
from typing import List, Dict, Type, TypeVar

from modelo import PacientePediatrico, Consulta, Medicion, MedicionFrecuenciaCardiaca, MedicionTemperatura, MedicionPeso, MedicionTalla

TMedicion = TypeVar('TMedicion', bound=Medicion)

class GestorUmbrales:
    """
    Servicio encargado de administrar los límites de umbrales de cada medición de forma dinámica.
    """

    def __init__(self):
        self._umbrales: Dict[Type[Medicion], Dict[str, float]] = {
            MedicionFrecuenciaCardiaca: {'minimo': 60.0, 'maximo': 120.0},
            MedicionTemperatura: {'minimo': 36.0, 'maximo': 37.5},
            MedicionPeso: {'minimo': 2.0, 'maximo': 150.0},
            MedicionTalla: {'minimo': 0.4, 'maximo': 2.0}
        }
    """
    Inicializador del servicio 'GestorUmbrales' para almacenar los límites de umbrales de cada medición.
    """
    
    def obtener_limites(self, tipo_medicion: Type[Medicion]) -> dict:
        """
        Método que retorna un diccionario con los límites (minimo y maximo) de cada medición.
        """
        try:
            return self._umbrales.get(tipo_medicion, {'minimo': 0, 'maximo': 0})
        except Exception as e:
            print(f'Error al obtener límites: {e}')
            return {'minimo': 0, 'maximo': 0}
    
    def configurar_limites(self, tipo_medicion: Type[Medicion], minimo: float, maximo: float) -> None:
        """
        Método para establecer los límites (minimo y maximo) de cada medición.
        """
        try:
            if minimo >= maximo:
                raise ValueError("El valor minimo debe ser menor que el valor maximo.")
            
            if tipo_medicion not in self._umbrales:
                self._umbrales[tipo_medicion] = {}
            
            self._umbrales[tipo_medicion]['minimo'] = float(minimo)
            self._umbrales[tipo_medicion]['maximo'] = float(maximo)
        except Exception as e:
            print(f'Error al configurar límites: {e}')

    def evaluar_valor(self, tipo_medicion: Type[Medicion], valor: float) -> bool:
        """
        Método que devuelve un 'true' si el valor está fuera de los límites del los umbrales. Devuelve un 'false' en caso contrario.
        """

        try:
            limites = self.obtener_limites(tipo_medicion)
            if limites['minimo'] == 0.0 and limites['minimo'] == 0.0:
                return False
        
            return valor < limites['minimo'] or valor > limites['maximo']
        except TypeError:
            return True #Si el dato es inválido, se manda un True por seguridad

    def guardar_estado(self, ruta_archivo: str) -> bool:
        """
        Método que guarda los umbrales configurados en un archivo para no perdelos.
        Retorna un true en caso de éxito, retorna un false en caso contrario.
        Recibe como parámetro la ruta completa del archivo (ubicación y nombre).
        """    
        try:
            dir = os.path.dirname(ruta_archivo)
            if dir and not os.path.exists(dir):
                os.makedirs(dir, exist_ok=True)
            with open(ruta_archivo, 'wb') as archivo:
                pickle.dump(self._umbrales, archivo)
            return True
        except IOError as e:
            print(f'Error al guardar archivo: {e}')
            return False
    
    def cargar_estado(self, ruta_archivo: str) -> bool:
        """
        Método que carga los umbrales configurados desde un archivo ya existente.
        Retorna un true en caso de éxito, retorna un false en caso contrario.
        Recibe como parámetro la ruta completa del archivo (ubicación y nombre).
        """
        try:
            if os.path.exists(ruta_archivo):
                with open(ruta_archivo, 'rb') as archivo:
                    datos = pickle.load(archivo)
                    if isinstance(datos, dict):
                        self._umbrales.update(datos)
                        return True
            return False
        except (pickle.PickleError, KeyError, EOFError) as e:
            print(f'Error al cargar archivo: {e}')
            return False

class GestorConsultas:
    """
    Servicio para administrar las instancias de la clase 'Consulta'.
    Evalua los datos directamente desde el repositorio de pacientes.
    """

    def __init__(self, repositorio):
        self._repositorio = repositorio

    def registrar_consultas(self, nueva_consulta: Consulta) -> bool:
        """
        Añade una nueva consulta al registro global.
        """
        try:
            paciente = nueva_consulta.paciente
            paciente.historial_consultas.append(nueva_consulta)
            self._repositorio.actualizar(paciente)
            return True
        except Exception as e:
            print(f'Error al registrar consulta: {e}')
            return False

    def obtener_consultas_por_doctor(self, cedula_doctor: str) -> List[Consulta]:
        """
        Método que devuelve un historial de consultas de un doctor en especifico. Regresa una lista vacía en caso de error.
        """
        consultas_encontradas = []
        try:
            for paciente in self._repositorio.leer_todos():
                for consulta in paciente.historial_consultas:
                    if consulta.doctor.cedula == cedula_doctor:
                        consultas_encontradas.append(consulta)
            return consultas_encontradas
        except Exception as e:
            print(f'Error al obtener consultas por doctor: {e}')
            return []
    
    def obtener_pacientes_por_doctor(self, cedula_doctor: str) -> List[PacientePediatrico]:
        """
        Método que devuelve un historial de pacientes de un doctor en especifico. Regresa una lista vacía en caso de error.
        """
        try:
            pacientes = {}
            for paciente in self._repositorio.leer_todos():
                for consulta in paciente.historial_consultas:
                    if consulta.doctor.cedula == cedula_doctor:
                        pacientes[paciente.curp] = paciente
            return list(pacientes.values())
        except Exception as e:
            print(f'Error al obtener pacientes por doctor: {e}')
            return []
    
    def obtener_consultas_por_paciente(self, curp_paciente: str) -> List[Consulta]:
        """
        Devuelve un historial de consultas de un paciente en especifico. Regresa una lista vacía en caso de error.
        """
        try:
            paciente = self._repositorio.leer(curp_paciente)
            return paciente.historial_consultas if paciente else []
        except Exception as e:
            print(f'Error al obtener consultas por paciente: {e}')
            return []
        
class AnalizadorEstadistico:
    """
    Servicio para analizar los valores de las mediciones de un paciente.
    """

    def __init__(self, paciente: PacientePediatrico):
        self._paciente = paciente

    def _extraer_valores(self, tipo_medicion: Type[TMedicion]) -> List[float]:
        """
        Método que extrae una lista general de los valores de un tipo de medicion en específico.
        """
        try:
            return [medicion.valor for medicion in self._paciente.historial if isinstance(medicion, tipo_medicion)]
        except Exception as e:
            print(f'Error al extraer valores: {e}')
            return []
    
    def calcular_promedio(self, tipo_medicion: Type[TMedicion]) -> float:
        """
        Método que calcula el promedio de todos los valores de un tipo de medicion en específico.
        """
        valores = self._extraer_valores(tipo_medicion)
        try:
            return float(statistics.mean(valores)) if valores else 0.0
        except statistics.StatisticsError as e:
            print(f'Error al calcular promedio: {e}')
            return 0.0
    
    def calcular_minimo(self, tipo_medicion: Type[TMedicion]) -> float:
        """
        Método que encuentra el mínimo de todos los valores de un tipo de medicion en específico.
        """
        valores = self._extraer_valores(tipo_medicion)
        try:
            return min(valores) if valores else 0.0
        except ValueError as e:
            print(f'Error al calcular minimo: {e}')
            return 0.0
    
    def calcular_maximo(self, tipo_medicion: Type[TMedicion]) -> float:
        """
        Método que encuentra el máximo de todos los valores de un tipo de medicion en específico.
        """
        valores = self._extraer_valores(tipo_medicion)
        try:
            return max(valores) if valores else 0.0
        except ValueError as e:
            print(f'Error al calcular maximo: {e}')
            return 0.0
    
    def calcular_desviacion_estandar(self, tipo_medicion: Type[TMedicion]) -> float:
        """
        Método que calcula la desviación estándar de todos los valores de un tipo de medicion en específico.
        """
        valores = self._extraer_valores(tipo_medicion)
        try:
            if len(valores) > 1:
                return float(statistics.stdev(valores))
            return 0.0
        except statistics.StatisticsError as e:
            print(f'Error al calcular desviación estándar: {e}')
            return 0.0
    
    def generar_reporte(self) -> dict:
        """
        Genera un diccionario compilado con todas las métricas de todas las mediciones.
        """
        tipos_a_evaluar: List[Type[Medicion]] = [MedicionFrecuenciaCardiaca, MedicionTemperatura, MedicionPeso, MedicionTalla]
        reporte = {}

        try:
            for tipo in tipos_a_evaluar:
                nombre_medicion = tipo.__name__.replace('Medicion', '')
                reporte[nombre_medicion] = {
                    'minimo': self.calcular_minimo(tipo),
                    'maximo': self.calcular_maximo(tipo),
                    'promedio': self.calcular_promedio(tipo),
                    'desviacion_estandar': self.calcular_desviacion_estandar(tipo)
                }
            return reporte
        except Exception as e:
            print(f'Error al generar reporte: {e}')
            return {}
        
    def exportar_reporte(self, ruta_archivo: str) -> bool:
        """
        Método para exportar el reporte generado en formato CSV
        """
        datos = self.generar_reporte()
        try:
            with open(ruta_archivo, mode='w', newline='', encoding='utf-8') as archivo:
                writer = csv.writer(archivo)
                writer.writerow(['Medición', 'Minimo', 'Máximo', 'Promedio', 'Desviación Estándar'])

                for medicion, metricas in datos.items():
                    writer.writerow([
                        medicion,
                        metricas['minimo'],
                        metricas['maximo'],
                        round(metricas['promedio'], 2),
                        round(metricas['desviacion_estandar'], 2)
                    ])
                return True
        except IOError as e:
            print(f'Error al exportar reporte: {e}')
            return False