import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

class Persona(ABC):
    """
    Clase abstracta base que encapsula la identidad general de la persona dentro del sistema.
    """

    def __init__(self, nombre: str, sexo: str, curp: str):
        self._nombre = nombre
        self._sexo = sexo
        self.curp = curp
    """
    Incializador de la clase 'Modelo' que recibe los datos generales de un individio cualquiera.
    :param nombre: Nombre completo de la persona
    :param sexo: Sexo de la persona
    :param curp: Curp de la persona
    """

    @property
    def curp(self) -> str:
        """
        Método que define el curp de la persona como propiedad.
        """
        return self._curp
    
    @curp.setter
    def curp(self, curp: str):
        self._curp = curp.strip().upper() if curp else ''
        if not self.verificar_curp():
            raise ValueError(f"El CURP '{curp}' no tiene un formato válido.")
    """
    Método que asigna el curp a la propiedad si al evaluar el curp es correcto. Si es así, lo asigna a la propiedad, en caso contrario manda un mensaje de error.
    """

    def verificar_curp(self) -> bool:
        """
        Método que evalua si el curp cumple con el formato correcto para retornar un 'true' si se cumple, retorna un 'false' en caso contrario.
        """
        patron = r"^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z\d]\d$"
        try:
            return bool(re.match(patron, self._curp))
        except TypeError:
            return False

    def __str__(self):
        """
        Método que devuelve en forma de cadena de texto los elementos de la persona: nombre, sexo, curp.
        """
        return f"{self._nombre} {self._sexo} {self._curp}"

class PersonalMedico(Persona, ABC):
    """
    Clase abstracta (Nivel 1 de herencia) que añade la identidad profesional de una persona dentro del sistema.
    """

    def __init__(self, nombre: str, sexo: str, curp: str, cedula: str):
        super().__init__(nombre, sexo, curp)
        self._cedula = cedula
    """
    Incializador de la clase 'PersonalMedico' que recibe los datos generales de un profesional.
    :param nombre: Nombre completo de la persona
    :param sexo: Sexo de la persona, caracter M o F
    :param curp: Curp de la persona
    :param cedula: Cedula de la persona
    """

    @property
    def cedula(self) -> str:
        """
        Método que define la cedula del profesionista como propiedad.
        """
        return self._cedula
    
    @cedula.setter
    def cedula(self, cedula: str):
        if not self.validar_credenciales():
            raise ValueError("La cedula debe ser alfanumerica")
        self._cedula = cedula.strip()
        """
        Método que evalua si la cedula del profesional es correcta para mandar un mensaje de error en caso de que así sea. En caso contrario lo asigna a la propiedad.
        """

    @abstractmethod
    def validar_credenciales(self) -> bool:
        """
        Método abstracto que evalua si la cedula del profesional es correcta para retornar un 'true' si se cumple, retorna un 'false' en caso contrario.
        """
        pass
        
    def __str__(self):
        """
        Método que devuelve en forma de cadena de texto los elementos de la persona: nombre, sexo, curp y cedula.
        """
        return f"{super().__str__()} {self.cedula}"
    
class Doctor(PersonalMedico):
    """
    Clase concreta (Nivel 2 de herencia) que especifica la identidad del Personal Medico como Doctor dentro del sistema.
    """

    def __init__(self, nombre: str, sexo: str, curp: str, cedula: str, consultorio: str):
        super().__init__(nombre, sexo, curp, cedula)
        self.consultorio = consultorio
        self._historial_pacientes: List[PacientePediatrico] = []
    """
    Inicializador de la clase 'Doctor' que recibe los datos generales de un doctor.
    :param nombre: Nombre completo de la persona.
    :param sexo: Sexo de la persona, caracter M o F.
    :param curp: Curp de la persona.
    :param cedula: Cedula de la persona.
    :param consultorio: Nombre del consultorio donde el doctor reside.
    """

    @property
    def historial_pacientes(self) -> List[PacientePediatrico]:
        """
        Definición de la propiedad historial_pacientes que almacena la historia de los pacientes que ha visitado el doctor. Retorna una lista de objetos PacientePediatrico.
        """
        return self._historial_pacientes
    
    @historial_pacientes.setter
    def historial_pacientes(self, historial_pacientes: List[PacientePediatrico]):
        """
        Método para asignar valores a la propiedad historial_pacientes que almacena la historia de los pacientes que ha visitado el doctor.
        Recibe una Lista de objetos PacientePediatrico.
        """
        self._historial_pacientes = historial_pacientes

    def validar_credenciales(self) -> bool:
        """
        Implementación del método abstracto validar_credenciales para validar la cedula del doctor.
        """
        return bool(self._cedula.isalnum() and len(self._cedula) == 8)

    def __str__(self):
        """
        Método que devuelve en forma de cadena de texto los elementos de la persona: nombre, sexo, curp y cedula.
        """
        return f"Dr. {super().__str__()} {self.consultorio}"
    

class PacientePediatrico(Persona):
    """
    Clase concreta para pacientes infantiles
    """
    def __init__(self, nombre: str, sexo: str, curp: str, fecha_nacimiento: str):
        super().__init__(nombre, sexo, curp)
        self.fecha_nacimiento = fecha_nacimiento
        self._edad = self.calcular_edad()
        self.historial: List[Medicion] = []
        self.historial_consultas: List[Consulta] = []
        """
        Inicializador de la clase 'PacientePediatrico' que recibe los datos generales de un paciente.
        :param nombre: Nombre completo de la persona.
        :param sexo: Sexo de la persona, caracter M o F.
        :param curp: Curp de la persona.
        :param fecha_nacimiento: Fecha de nacimiento del paciente.
        """

    @property 
    def edad(self) -> int:
        return self._edad
    
    def calcular_edad(self) -> int:
        """
        Método para calcular la edad del paciente en base al año de su fecha de nacimiento. Retorna la edad del paciente.
        """
        try:
            fecha_nac = datetime.strptime(self.fecha_nacimiento, "%d-%m-%Y")
            hoy = datetime.now()
            return hoy.year - fecha_nac.year - ((hoy.month, hoy.day)< (fecha_nac.month, fecha_nac.day))
        except ValueError:
            return 0
    
    @classmethod
    def desde_cadena(cls, cadena_csv: str) -> 'PacientePediatrico':
        """
        Método de fábrica para crear un objeto PacientePediatrico a partir de una cadena de texto con la información del paciente.
        """
        try:
            slices = cadena_csv.split(',')
            return cls(
                nombre=slices[0].strip(),
                curp=slices[1].strip(),
                sexo=slices[2].strip(),
                fecha_nacimiento=slices[3].strip()
            )
        except IndexError as e:
            raise ValueError(f"La cadena de texto no tiene la información necesaria para crear el paciente: {e}")

    def __str__(self):
        """
        Método que devuelve en forma de cadena de texto los elementos del paciente: nombre, sexo, curp, fecha de nacimiento, edad, historial de mediciones e historial de consultas.
        """
        return f"{super().__str__()} {self.fecha_nacimiento} {self._edad} {self.historial} {self.historial_consultas}"

class Consulta():
    """
    Clase que representa una consulta realizada por un doctor a un paciente.
    """
    
    def __init__(self, fecha: str, doctor: Doctor, paciente: PacientePediatrico):
        self.fecha = fecha
        self.doctor = doctor
        self.paciente = paciente

    def __str__(self) -> str:
        return f"Consulta: {self.fecha} - Dr. {self.doctor._nombre} - Paciente {self.paciente._nombre}"


class Medicion(ABC):
    """
    Clase abstracta base para todas las mediciones que se le realizan a un paciente.
    """

    def __init__(self, fecha: str, valor: float):
        self.valor = valor
        self.fecha = fecha
        """
        Inicializador de la clase 'Medicion' que recibe la fecha generada de manera automática y la formatea en d-m-Y H:M:S.
        :param fecha: Fecha generada de manera automática.
        """
    
    @abstractmethod
    def en_riesgo(self, gestor_umbrales) -> bool:
        """
        Método abstracto que evalua si el valor de la medición entra en un rango de riesgo para retornar un 'true' si se cumple, retorna un 'false' en caso contrario.
        """
        pass
    
    @staticmethod
    def celsius_to_fahrenheit(grados_celsius:float) -> float:
        """
        Método estático para convertir grados Celsius a grados Fahrenheit.
        :param grados_celsius: Grados Celsius.
        :return: Grados Fahrenheit.
        """
        return (grados_celsius * 9/5) + 32
    
    @staticmethod
    def kg_to_lbs(kg: float) -> float:
        """
        Método estático para convertir kg a libras.
        :param kg: kg.
        :return: Libras.
        """
        return kg * 2.20462
    
class MedicionFrecuenciaCardiaca(Medicion):
    """
    Clase concreta para la evaluacuín de la frecuencia cardiaca del paciente.
    """

    def en_riesgo(self, gestor_umbrales) -> bool:
        """
        Implementación del método abstracto en_riesgo para evaluar si la frecuencia cardiaca del paciente entra en un rango de riesgo.
        Retorna un 'true' si se cumple, retorna un 'false' en caso contrario.
        """
        return gestor_umbrales.evaluar_valor(type(self), self.valor)
    
class MedicionTemperatura(Medicion):
    """
    Clase concreta para la evaluación de la temperatura corporal del paciente.
    """

    def en_riesgo(self, gestor_umbrales) -> bool:
        """
        Implementación del método abstracto en_riesgo para evaluar si la temperatura corporal del paciente entra en un rango de riesgo.
        Retorna un 'true' si se cumple, retorna un 'false' en caso contrario.
        """
        return gestor_umbrales.evaluar_valor(type(self), self.valor)

class MedicionPeso(Medicion):
    """
    Clase concreta para la evaluación del peso del paciente.
    """

    def en_riesgo(self, gestor_umbrales) -> bool:
        """
        Implementación del método abstracto en_riesgo para evaluar si el peso del paciente entra en un rango de riesgo.
        Retorna un 'true' si se cumple, retorna un 'false' en caso contrario.
        """
        return gestor_umbrales.evaluar_valor(type(self), self.valor)
    

class MedicionTalla(Medicion):
    """
    Implementación de la clase 'Medicion' para la evaluación de la altura del paciente.
    """

    def en_riesgo(self, gestor_umbrales) -> bool:
        """
        Implementación del método abstracto en_riesgo para evaluar si la altura del paciente entra en un rango de riesgo.
        Retorna un 'true' si se cumple, retorna un 'false' en caso contrario.
        """
        return gestor_umbrales.evaluar_valor(type(self), self.valor)