# SiSI
Sistema de Seguimiento de Indicadores de Salud Infantil, desarrollador con Pyhton

Un sistema integral de escritorio (GUI) desarrollado en Python para la administración de expedientes clínicos pediátricos, control biométrico y agenda de consultas médicas. Diseñado con un enfoque estricto en la Arquitectura de Software, Programación Orientada a Objetos (POO) y tipado estático.

# 🚀 Características Principales
- Gestión de Pacientes (CRUD Completo): Registro, actualización y eliminación de pacientes con validación estricta de formato oficial mediante expresiones regulares (CURP).
- Expediente Biométrico Avanzado: Seguimiento de temperatura, frecuencia cardíaca, peso y talla. El sistema alerta automáticamente si los indicadores del paciente se encuentran fuera de los umbrales de riesgo médicos configurables.
- Agenda de Consultas: Integración de un sistema de agendado de citas por doctor, utilizando selectores de fecha (tkcalendar) y tiempo interactivos.
- Análisis Estadístico y Reportes: Generación automática de métricas clínicas (promedios, máximos, mínimos y desviación estándar) con capacidad de exportación a archivos .csv.
- Persistencia Segura y Asíncrona: Guardado y carga de datos binarios en segundo plano garantizando que la interfaz gráfica nunca se congele, además de persistencia inmediata al agendar citas para prevenir pérdida de información ante cierres abruptos.

# 🏗️ Arquitectura y Patrones de Diseño
El proyecto fue construido siguiendo rigurosamente diagramas UML, garantizando una separación clara de responsabilidades:
- modelo.py: Clases de dominio puras y abstractas (e.g., Persona, PacientePediatrico, Medicion). Uso extensivo de propiedades (@property / @setter) para el encapsulamiento y métodos de fábrica (@classmethod).
- repositorio.py: Capa de acceso a datos que maneja la serialización binaria (pickle) para el estado de los pacientes.
- servicios.py: Lógica de negocio orquestada. Destaca la implementación de relaciones débiles (dependencia) entre componentes (por ejemplo, entre GestorConsultas y la entidad Consulta) para interactuar con los datos a través del repositorio sin duplicar memoria.
- app.py: Controlador de la interfaz gráfica implementado bajo el patrón Maestro-Detalle y contenedor de vistas apiladas.
- Concurrencia (Threading): Implementación del módulo threading coordinado con el mainloop de Tkinter a través de self.after para evitar condiciones de carrera (Race Conditions) durante las operaciones de Entrada/Salida (I/O).

# 🛡️ Calidad de Código (Tipado Estricto)
- Uso de Optional[T] para manejo seguro de nulos en búsquedas del repositorio.
- Definición clara de colecciones como Dict[str, tk.StringVar] y List[Consulta].
- Estrechamiento de tipos (Type Narrowing) para la evaluación lógica segura.

# 💻 Tecnologías Utilizadas
- Lenguaje: Python 3.10+
- Interfaz Gráfica: tkinter (Librería estándar) y ttk (Notebooks, Treeviews, Comboboxes).
- Componentes Visuales de Terceros: tkcalendar (DatePickers).
- Persistencia: pickle, manipulación de sistema de archivos (os).
- Utilidades: datetime, re (Expresiones regulares para validación de identidad).

📂 Estructura del Proyecto

/</br>
├── main.py               # Punto de entrada de la aplicación </br>
├── app.py                # Interfaz gráfica (Vistas y Controladores GUI)</br>
├── modelo.py             # Entidades del dominio y lógica de validación</br>
├── repositorio.py        # Persistencia de datos en disco</br>
├── servicios.py          # Gestores de lógica de negocio (Consultas, Umbrales, Reportes)</br>
├── datos/                # (Generado automáticamente) Base de datos local</br>
│   ├── umbrales.pkl      # Configuración de límites médicos guardados</br>
│   └── (archivos CSV de reportes exportados)</br>
└── README.md</br>
