import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime
from typing import Optional, Dict
from tkcalendar import DateEntry # type: ignore

from modelo import PacientePediatrico, MedicionFrecuenciaCardiaca, MedicionTemperatura, MedicionPeso, MedicionTalla, Doctor, Consulta
from repositorio import RepositorioPacientes
from servicios import GestorUmbrales, GestorConsultas, AnalizadorEstadistico

class App(tk.Tk):
    """
    Controlador principal de la apliación. Hereda de Tkinter y gestiona el ciclo de vida, la persistencia y las diferentes vistas de la aplicación.
    """

    def __init__(self):
        super().__init__()
        self._inicializar_dependencias()
        self._configurar_interfaz()
        self._iniciar_vistas()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _inicializar_dependencias(self):
        """
        Método que inicializa las capas de datos y servicios.
        """
        self._repositorio_pacientes = RepositorioPacientes()
        self._gestor_umbrales = GestorUmbrales()
        self._gestor_consultas = GestorConsultas(self._repositorio_pacientes)
        self.doctor = Doctor('G. House', 'M', 'DRHS090807HVZRDLA4', '12345678', 'Consultorio 1') # type: ignore

        hilo_carga = threading.Thread(target=self._cargar_datos)
        hilo_carga.start()

    def _cargar_datos(self):
        """
        Método de carga de datos en segundo plano. Se ejecuta en un hilo separado para no bloquear la interfaz.
        """
        try:
            self._repositorio_pacientes.cargar_estado('data/pacientes.pkl')
            self._gestor_umbrales.cargar_estado('data/umbrales.pkl')
            print('Datos cargados exitosamente.')
        except Exception as e:
            print(f'Error al cargar datos: {e}')
    
    def _configurar_interfaz(self):
        """
        Método que configura la interfaz de la aplicación.
        """
        self.title('Sistema de Salud Infantil - SiSI')
        self.geometry('900x600')
        self.vistas = {}
        self._vista_actual = None
        self.contenedor = tk.Frame(self)
        self.contenedor.pack(side='top', fill='both', expand=True)
        self.contenedor.grid_rowconfigure(0, weight=1)
        self.contenedor.grid_columnconfigure(0, weight=1)
    
    def _iniciar_vistas(self):
        """
        Instancia todas las vistas de la aplicación y las guarda en un contenedor.
        """
        for ClaseVista in (VistaMediciones, VistaReporte, VistaConfiguracionUmbrales, VistaPacientes):
            nombre_vista = ClaseVista.__name__
            frame = ClaseVista(parent=self.contenedor, controlador=self)
            self.vistas[nombre_vista] = frame
            frame.grid(row=0, column=0, sticky='nsew')
        self.update_idletasks()
        self.mostrar_vista('VistaPacientes')

    def mostrar_vista(self, nombre_vista: str, **kwargs):
        """
        Método para la nevegación funcional entre las vistas de la aplicación.
        Recibe como parámetro el nombre de la vista a mostrar y permite pasar argumentos a las vistas.
        """
        vista = self.vistas.get(nombre_vista)
        if vista:
            if hasattr(vista, 'cargar_info_paciente') and 'curp' in kwargs:
                vista.cargar_info_paciente(kwargs['curp'])
            elif hasattr(vista, 'cargar_info_reporte') and 'curp' in kwargs:
                vista.cargar_info_reporte(kwargs['curp'])

            self._vista_actual = vista
            vista.tkraise()
            if hasattr(vista, '_actualizar_tabla'):
                vista._actualizar_tabla()
    
    def iniciar(self):
        """
        Método que arranca el mainloop de tkinter.
        """
        self.mainloop()

    def on_close(self):
        """
        Método que se ejecuta al cerrar la aplicación. Se implementa el uso de threading para guardar en segundo plano los datos sin bloquear la aplicación, evitar caídas del sistema o pérdida de datos.
        """
        def _guardar_datos():
            try:
                self._repositorio_pacientes.guardar_estado('data/pacientes.pkl')
                self._gestor_umbrales.guardar_estado('data/umbrales.pkl')
                print('Guardado en segundo plano exitosamente.')
            except Exception as e:
                print(f'Error al guardar datos: {e}')
        
        def _verificar_y_cerrar():
            """
            Método recursivo que verifica si el hilo de guardado de datos está en ejecución y, en caso contrario, lo cierra.
            """
            if hilo_guardar.is_alive():
                self.after(100, _verificar_y_cerrar)
            else:
                self.quit()
                self.destroy()

        messagebox.showinfo('Cerrando...', 'Guardando datos...', parent=self)
        hilo_guardar = threading.Thread(target=_guardar_datos)
        hilo_guardar.start()
        _verificar_y_cerrar()

class VistaPacientes(tk.Frame):
    """
    Pantalla Principal de gestión de los pacientes.
    """

    def __init__(self, parent, controlador: App):
        super().__init__(parent)
        self._controlador = controlador
        self._repositorio = controlador._repositorio_pacientes
        self._entradas: Dict[str, tk.StringVar] = {}
        self._curp_seleccionado: Optional[str] = None
        self._configurar_interfaz()

    def _configurar_interfaz(self):
        """
        Método para configurar todos los elementos visuales de la interfaz.
        """
        lbl_titulo = tk.Label(self, text='Gestión de Pacientes Pediátricos', font=('Arial', 18, 'bold'))
        lbl_titulo.pack(pady=10)
        frame_form = tk.Frame(self)
        frame_form.pack(pady=5)
        tk.Label(frame_form, text='Nombre:').grid(row=0, column=0, padx=5, pady=5)
        self._entradas['nombre'] = tk.StringVar()
        tk.Entry(frame_form, textvariable=self._entradas['nombre']).grid(row=0, column=1)

        tk.Label(frame_form, text='Sexo:').grid(row=0, column=2, padx=5, pady=5)
        self._entradas['sexo'] = tk.StringVar(value='M')
        frame_sexo = tk.Frame(frame_form)
        frame_sexo.grid(row=0, column=3, sticky='w')
        tk.Radiobutton(frame_sexo, text='Masculino', variable=self._entradas['sexo'], value='M').pack(side='left')
        tk.Radiobutton(frame_sexo, text='Femenino', variable=self._entradas['sexo'], value='F').pack(side='left', padx=5)

        tk.Label(frame_form, text='CURP:').grid(row=1, column=0, padx=5, pady=5)
        self._entradas['curp'] = tk.StringVar()
        tk.Entry(frame_form, textvariable=self._entradas['curp']).grid(row=1, column=1)

        tk.Label(frame_form, text='Fecha de nacimiento:').grid(row=1, column=2, padx=5, pady=5)
        self._entradas['fecha'] = tk.StringVar()
        calendario = DateEntry(
            frame_form,
            textvariable=self._entradas['fecha'],
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='dd-mm-yyyy',
            state='readonly'
        )
        calendario.grid(row=1, column=3, padx=5)

        frame_botones = tk.Frame(self)
        frame_botones.pack(pady=10)
        tk.Button(frame_botones, text='Guardar Paciente', command=self._evt_guardar_paciente, bg='lightgreen').pack(side='left', padx=5)
        tk.Button(frame_botones, text='Actualizar', command=self._evt_actualizar_paciente, bg='lightblue').pack(side='left', padx=5)
        tk.Button(frame_botones, text='Eliminar', command=self._evt_eliminar_paciente, bg='lightcoral').pack(side='left', padx=5)
        tk.Label(frame_botones, text='|', font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        tk.Button(frame_botones, text='Ver Mediciones', command=self._evt_ver_historial).pack(side='left', padx=5)
        tk.Button(frame_botones, text='Generar Reporte', command=self._evt_ver_reporte).pack(side='left', padx=5)
        tk.Button(frame_botones, text='Configurar Umbrales', command=lambda: self._controlador.mostrar_vista('VistaConfiguracionUmbrales')).pack(side='left', padx=5)

        cols = ('nombre', 'curp', 'sexo', 'edad')
        self._tabla_pacientes = ttk.Treeview(self, columns=cols, show='headings')
        for col in cols:
            self._tabla_pacientes.heading(col, text=col.capitalize())
        self._tabla_pacientes.pack(fill='both', expand=True, padx=20, pady=10)
        self._tabla_pacientes.bind('<<TreeviewSelect>>', self._evt_seleccionar_paciente)

    def _evt_guardar_paciente(self):
        """
        Método de evento para guardar un paciente en el sistema.
        """
        nombre = self._entradas['nombre'].get().strip()
        curp = self._entradas['curp'].get().strip()
        if not nombre or not curp:
            messagebox.showwarning('Aviso', 'Debe ingresar todos los datos del paciente.')
            return
        
        try:
            cadena_csv = f"{self._entradas['nombre'].get()},{self._entradas['curp'].get()},{self._entradas['sexo'].get()},{self._entradas['fecha'].get()}"
            nuevo_paciente = PacientePediatrico.desde_cadena(cadena_csv)
            exito = self._repositorio.crear(nuevo_paciente)
            if exito:
                messagebox.showinfo('Éxito', 'Paciente guardo exitosamente.')
                self._actualizar_tabla()
                self._limpiar_formulario()
            else:
                messagebox.showerror('Error', 'El CURP ya existe en el sistema.')
        except ValueError as ve:
            messagebox.showwarning("Validación", str(ve))
        except Exception as e:
            messagebox.showerror('Error. Está mal en algo.', str(e))
    
    def _evt_actualizar_paciente(self):
        """
        Método para actualizar los datos de un pacientes en el sistema.
        """
        if not self._curp_seleccionado:
            messagebox.showwarning('Seleccione un paciente', 'Seleccione un paciente de la tabla.')
            return
        
        nombre = self._entradas['nombre'].get().strip()
        curp_nuevo = self._entradas['curp'].get().strip()
        sexo = self._entradas['sexo'].get().strip()
        fecha = self._entradas['fecha'].get().strip()
        if not nombre or not curp_nuevo:
            messagebox.showwarning('Campos Vacíos', 'Seleccione un paciente de la tabla.')
            return
        
        paciente_antiguo = self._repositorio.leer(self._curp_seleccionado)

        if not paciente_antiguo:
            messagebox.showwarning('Paciente No Encontrado', 'El paciente original no existe.')
            return
        
        if curp_nuevo != self._curp_seleccionado:
            if self._repositorio.leer(curp_nuevo):
                messagebox.showwarning('Paciente Ya Existe', 'El paciente con el curp seleccionado ya existe.')
                return
        try:
            cadena_csv = f"{nombre},{curp_nuevo},{sexo},{fecha}"
            paciente_actualizado = PacientePediatrico.desde_cadena(cadena_csv)
            paciente_actualizado.historial = paciente_antiguo.historial
            paciente_actualizado.historial_consultas = paciente_antiguo.historial_consultas

            if curp_nuevo != self._curp_seleccionado:
                self._repositorio.eliminar(self._curp_seleccionado)
                exito = self._repositorio.crear(paciente_actualizado)
            else:
                exito = self._repositorio.actualizar(paciente_actualizado)
            
            if exito:
                messagebox.showinfo('Éxito', 'Paciente actualizado exitosamente.')
                self._limpiar_formulario()
                self._actualizar_tabla()
            else:
                messagebox.showerror('Error', 'Error al actualizar el paciente.')
        except ValueError as ve:
            messagebox.showwarning("Validación", f'Datos Incorrectos: {ve}')
        except Exception as e:
            messagebox.showerror('Error. Está mal en algo.', str(e))

    def _actualizar_tabla(self):
        """
        Método que limpia la tabla de pacientes y la vuelve a llenar.
        """
        for item in self._tabla_pacientes.get_children():
            self._tabla_pacientes.delete(item)
        for paciente in self._repositorio.leer_todos():
            self._tabla_pacientes.insert('', 'end', values=(paciente._nombre, paciente._curp, paciente._sexo, paciente._edad))
    
    def _evt_seleccionar_paciente(self, event):
        """
        Método para seleccionar un paciente en específico.
        """
        seleccion = self._tabla_pacientes.selection()
        if not seleccion: return
        curp = self._tabla_pacientes.item(seleccion[0])['values'][1]
        paciente = self._repositorio.leer(curp)
        if paciente:
            self._entradas['nombre'].set(paciente._nombre)
            self._entradas['curp'].set(paciente.curp)
            self._entradas['sexo'].set(paciente._sexo)
            self._entradas['fecha'].set(paciente.fecha_nacimiento)
            self._curp_seleccionado = paciente.curp
        

    def _evt_ver_historial(self):
        """
        Método para ver el historial de un paciente en específico.
        """
        seleccion = self._tabla_pacientes.selection()
        if not seleccion:
            messagebox.showwarning('Aviso', 'Seleccione un paciente de la tabla.')
            return
        curp = self._tabla_pacientes.item(seleccion[0])['values'][1]
        self._controlador.mostrar_vista('VistaMediciones', curp=curp)

    def _evt_ver_reporte(self):
        """
        Método para ver el reporte de las mediciones de un paciente en específico.
        """
        seleccion = self._tabla_pacientes.selection()
        if not seleccion:
            messagebox.showwarning('Aviso', 'Seleccione un paciente de la tabla.')
            return
        curp = self._tabla_pacientes.item(seleccion[0])['values'][1]
        self._controlador.mostrar_vista('VistaReporte', curp=curp)
    
    def _evt_eliminar_paciente(self):
        """
        Método para eliminar un paciente del sistema.
        """
        seleccion = self._tabla_pacientes.selection()
        if not seleccion:
            messagebox.showwarning('Aviso', 'Seleccione un paciente de la tabla.')
            return
        curp = self._tabla_pacientes.item(seleccion[0])['values'][1]
        respuesta = messagebox.askyesno('Confirmación', '¿Está seguro de eliminar el paciente?')
        if respuesta:
            exito = self._repositorio.eliminar(curp)
            if exito:
                messagebox.showinfo('Éxito', 'Paciente eliminado exitosamente.')
                self._actualizar_tabla()
            else:
                messagebox.showerror('Error', 'Error al eliminar el paciente.')
    
    def _limpiar_formulario(self):
        """
        Método para limpiar el formulario de registro de pacientes.
        """
        self._entradas['nombre'].set('')
        self._entradas['curp'].set('')
        self._entradas['sexo'].set('M')
        self._entradas['fecha'].set('')
        self._curp_seleccionado = None

class VistaMediciones(tk.Frame):
    """
    Vista para registrar las mediciones de un paciente y ver su historial.
    """

    def __init__(self, parent, controlador: App):
        super().__init__(parent)
        self._controlador = controlador
        self._repositorio = controlador._repositorio_pacientes
        self._gestor_umbrales = controlador._gestor_umbrales
        self._gestor_consultas = controlador._gestor_consultas
        self._curp_actual = ''
        self._tipo_medicion = tk.StringVar(value='Frecuencia Cardiaca')
        self._valor = tk.DoubleVar()
        self._configurar_interfaz()

    def _configurar_interfaz(self):
        """
        Método para configurar la interfaz de esta vista.
        """
        self.lbl_titulo = tk.Label(self, text='', font=('Arial', 18, 'bold'))
        
        self.lbl_titulo.pack(pady=10)

        self.lbl_alerta = tk.Label(self, text='', font=('Arial', 10, 'bold'))
        self.lbl_alerta.pack(pady=10)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=10)
        self.tab_mediciones = tk.Frame(self.notebook)
        self.tab_consultas = tk.Frame(self.notebook)
        self.notebook.add(self.tab_mediciones, text='Mediciones')
        self.notebook.add(self.tab_consultas, text='Historial de Consultas')
        self._configurar_tab_mediciones()
        self._configurar_tab_consultas()

        tk.Button(self, text='Regresar al Menú Pacientes', command=self.evt_regresar).pack(pady=10)

    def _configurar_tab_mediciones(self):
        """
        Metodo para configurar la pestaña de las mediciones de los pacientes.
        """
        frame_form = tk.Frame(self.tab_mediciones)
        frame_form.pack(pady=5)

        tk.Label(frame_form, text='Medicion:').grid(row=0, column=0)
        cmb_medicion = ttk.Combobox(frame_form, textvariable=self._tipo_medicion, state='readonly')
        cmb_medicion['values'] = ('Frecuencia Cardiaca', 'Temperatura', 'Peso', 'Talla')
        cmb_medicion.grid(row=0, column=1, padx=5)

        tk.Label(frame_form, text='Valor:').grid(row=0, column=2)
        tk.Entry(frame_form, textvariable=self._valor, width=10).grid(row=0, column=3, padx=5)

        tk.Button(frame_form, text='Guardar Medición', command=self._evt_guardar_medicion).grid(row=0, column=6, padx=10)

        self._tabla_mediciones = ttk.Treeview(self, columns=('Fecha', 'Medición', 'Valor', 'Estado'), show='headings')
        for col in ('Fecha', 'Medición', 'Valor', 'Estado'):
            self._tabla_mediciones.heading(col, text=col.capitalize())
        
        self._tabla_mediciones.tag_configure('riesgo', background='#ffcccc')
        self._tabla_mediciones.pack(fill='both', expand=True, padx=20, pady=10)

    def _configurar_tab_consultas(self):
        """
        Método para configurar la pestaña de los historiales de consultas de los pacientes.
        """
        frame_form = tk.Frame(self.tab_consultas)
        frame_form.pack(pady=10)

        doc = self._controlador.doctor
        tk.Label(frame_form, text=f'Dr.{doc._nombre} | {doc.consultorio}', font=('Arial', 18, 'bold')).grid(row=0, column=0, padx=15, pady=5)

        tk.Label(frame_form, text='Fecha:').grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self._cal_consulta = DateEntry(frame_form, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd-mm-yyyy', state='readonly')
        self._cal_consulta.grid(row=2, column=1, padx=5, pady=5, sticky='w')

        tk.Label(frame_form, text='Hora:').grid(row=2, column=2, padx=5, pady=5, sticky='e')
        frame_tiempo = tk.Frame(frame_form)
        frame_tiempo.grid(row=2, column=3, sticky='w')
        self._cmb_hora = ttk.Combobox(frame_tiempo, state='readonly', width=3, values=[f'{i:02}' for i in range(24)])
        self._cmb_hora.set('00')
        self._cmb_hora.pack(side='left')
        tk.Label(frame_tiempo, text=':').pack(side='left')
        self._cmb_minutos = ttk.Combobox(frame_tiempo, state='readonly', width=3, values=['00','15','30','45'])
        self._cmb_minutos.set('00')
        self._cmb_minutos.pack(side='left')
        tk.Button(frame_form, text='Agendar Consulta', command=self._evt_registrar_consulta, bg='lightblue').grid(row=1, column=4, rowspan=2, padx=15)

        self._tabla_consultas = ttk.Treeview(self, columns=('Fecha', 'Consultorio'), show='headings')
        for col in ('Fecha', 'Consultorio'):
            self._tabla_consultas.heading(col, text=col.capitalize())

        self._tabla_consultas.heading('Fecha', text='Fecha y Hora')
        self._tabla_consultas.heading('Consultorio', text='Consultorio')
        self._tabla_consultas.pack(fill='both', expand=True, padx=10, pady=10)

    def _evt_registrar_consulta(self):
        """
        Método para registrar una nueva consulta.
        """
        paciente = self._repositorio.leer(self._curp_actual)
        if not paciente:
            messagebox.showwarning('Aviso', 'No hay un paciente seleccionado.')
            return
    
        doc = self._controlador.doctor
        fecha_cal = self._cal_consulta.get()
        hora = self._cmb_hora.get()
        min = self._cmb_minutos.get()
        fecha_completa = f'{fecha_cal} {hora}:{min}'
        if not fecha_cal:
            messagebox.showwarning('Aviso', 'Debe seleccionar una fecha para la consulta.')
            return
        nueva_consulta = Consulta(fecha_completa, doc, paciente)
        exito = self._gestor_consultas.registrar_consultas(nueva_consulta)
        if exito:
            messagebox.showinfo('Éxito', 'Consulta registrada exitosamente.')
            self._actualizar_tabla_consultas()
            self._cmb_hora.set('00')
            self._cmb_minutos.set('00')
        else:
            messagebox.showerror('Error', 'Error al registrar la consulta.')

    def cargar_info_paciente(self, curp: str):
        self._curp_actual = curp
        paciente = self._repositorio.leer(curp)
        if paciente:
            self.lbl_titulo.config(text=f'Historial del {paciente._nombre} CURP: {paciente._curp}')
            self._actualizar_tabla()
            self._actualizar_tabla_consultas()
    
    def _actualizar_tabla(self):
        for item in self._tabla_mediciones.get_children():
            self._tabla_mediciones.delete(item)
        
        paciente = self._repositorio.leer(self._curp_actual)
        hay_riesgo_general = False

        if paciente:
            for med in paciente.historial:
                es_riesgo = med.en_riesgo(self._gestor_umbrales)
                estado = 'ALERTA RIESGO' if es_riesgo else 'OK'
                tag = ('riesgo',) if es_riesgo else ()
                if es_riesgo: hay_riesgo_general = True
                tipo_nombre = type(med).__name__.replace('Medicion', '')
                self._tabla_mediciones.insert('', 'end', values=(med.fecha, tipo_nombre, med.valor, estado), tags=tag)

        if hay_riesgo_general:
            self.lbl_alerta.config(text='¡ATENCIÓN! El Paciente presenta mediciones fuera de los umbrales normales.')
        else:
            self.lbl_alerta.config(text='')
    
    def _actualizar_tabla_consultas(self):
        """
        Método para actualizar la tabla de consultas.
        """
        for item in self._tabla_consultas.get_children():
            self._tabla_consultas.delete(item)
        
        consultas_paciente = self._gestor_consultas.obtener_consultas_por_paciente(self._curp_actual)
        consultas_paciente.sort(key=lambda x: x.fecha, reverse=True)
        for consulta in consultas_paciente:
            self._tabla_consultas.insert('', 'end', values=(consulta.fecha, consulta.doctor.consultorio))

    def _evt_guardar_medicion(self):
        try:
            paciente = self._repositorio.leer(self._curp_actual)
            if not paciente: return
            tipo = self._tipo_medicion.get()
            valor = self._valor.get()
            fecha = datetime.now().strftime('%d-%m-%Y %H:%M')
            dic_clases = {
                'FrecuenciaCardiaca': MedicionFrecuenciaCardiaca,
                'Temperatura': MedicionTemperatura,
                'Peso': MedicionPeso,
                'Talla': MedicionTalla
            }
            clase_seleccionada = dic_clases[tipo]
            nueva_medicion = clase_seleccionada(fecha, valor)
            paciente.historial.append(nueva_medicion)
            self._repositorio.actualizar(paciente)
            self._actualizar_tabla()
            self._valor.set(0.0)
        except ValueError as ve:
            messagebox.showwarning("Validación", f'Datos Incorrectos: {ve}')
        except Exception as e:
            messagebox.showerror('Error. Está mal en algo.', str(e))
    
    def evt_regresar(self):
        """
        Método para regresar al menú principal.
        """
        self._controlador.mostrar_vista('VistaPacientes')

class VistaReporte(tk.Frame):
    """
    Vetana para mostrar las analíticas de las mediciones de los pacientes.
    """

    def __init__(self, parent, controlador: App):
        super().__init__(parent)
        self._controlador = controlador
        self._repositorio = controlador._repositorio_pacientes
        self._curp_actual = ''
        self._analizador_actual: Optional[AnalizadorEstadistico] = None
        self._configurar_interfaz()

    def _configurar_interfaz(self):
        """
        Método para configurar la interfaz de esta vista.
        """
        self._lbl_titulo = tk.Label(self, text='Reporte Estadístico', font=('Arial', 18, 'bold'))
        self._lbl_titulo.pack(pady=10)

        cols = ('Medición', 'Minimo', 'Máximo', 'Promedio', 'Desviación Estándar')
        self._tabla_reporte = ttk.Treeview(self, columns=cols, show='headings')

        for col in cols:
            self._tabla_reporte.heading(col, text=col.capitalize())
        self._tabla_reporte.pack(fill='both', expand=True, padx=20, pady=10)

        frame_botones = tk.Frame(self)
        frame_botones.pack(pady=10)
        tk.Button(frame_botones, text='Exportar a CSV', command=self._evt_exportar_csv).pack(side='left', padx=10)
        tk.Button(frame_botones, text='Regresar', command=self.evt_regresar).pack(side='left', padx=10)

    def cargar_info_reporte(self, curp: str):
        """
        Método para cargar la información de un paciente en específico.
        """
        self._curp_actual = curp
        paciente = self._repositorio.leer(self._curp_actual)
        if paciente:
            self._lbl_titulo.config(text=f'Reporte Estadístico de {paciente._nombre} CURP: {paciente._curp}')
            self._generar_y_mostrar_stats(paciente)
    
    def _generar_y_mostrar_stats(self, paciente: PacientePediatrico):
        """
        Método que genera y muestra los datos de un paciente en específico.
        """
        try:
            for item in self._tabla_reporte.get_children():
                self._tabla_reporte.delete(item)
            
            self._analizador_actual = AnalizadorEstadistico(paciente)
            reporte = self._analizador_actual.generar_reporte()

            for indicador, metricas in reporte.items():
                self._tabla_reporte.insert('', 'end', values=(indicador, f'{metricas['minimo']:.2f}', f'{metricas['maximo']:.2f}', f'{metricas['promedio']:.2f}', f'{metricas['desviacion_estandar']:.2f}'))
        except Exception as e:
            messagebox.showerror('Error', 'Error al generar reporte. Está mal en algo.', parent=self)
        
    def _evt_exportar_csv(self):
        """
        Método para exportar el reporte generado en formato CSV.
        """
        if not self._analizador_actual: return
        try:
            ruta = f'data/reporte_{self._curp_actual}.csv'
            exito = self._analizador_actual.exportar_reporte(ruta)
            if exito:
                messagebox.showinfo('Éxito', 'Reporte exportado exitosamente.')
            else:
                messagebox.showerror('Error', 'Error al exportar el reporte.')
        except Exception as e:
            messagebox.showerror('Error', 'Error al exportar el reporte. Está mal en algo.', parent=self)

    def evt_regresar(self):
        """
        Método para regresar al menú principal.
        """
        self._analizador_actual = None
        self._controlador.mostrar_vista('VistaPacientes')

class VistaConfiguracionUmbrales(tk.Frame):
    """
    Ventana de administración de los umbrales de mediciones.
    """
    def __init__(self, parent, controlador: App):
        super().__init__(parent)
        self._controlador = controlador
        self._gestor_umbrales = controlador._gestor_umbrales
        self._tipo_medicion = tk.StringVar(value='Temperatura')
        self._valor_minimo = tk.DoubleVar()
        self._valor_maximo = tk.DoubleVar()
        self._configurar_interfaz()

    def _configurar_interfaz(self):
        tk.Label(self, text='Administración de umbrales de mediciones', font=('Arial', 18, 'bold')).pack(pady=20)
        frame = tk.Frame(self)
        frame.pack(pady=10)

        tk.Label(frame, text='Seleccione la medición:').grid(row=0, column=0, pady=10)
        cmb_medicion = ttk.Combobox(frame, textvariable=self._tipo_medicion, state='readonly')
        cmb_medicion['values'] = ('Frecuencia Cardiaca', 'Temperatura', 'Peso', 'Talla')
        cmb_medicion.grid(row=0, column=1, padx=10)
        cmb_medicion.bind('<<ComboboxSelected>>', self.evt_seleccionar_medicion)

        tk.Label(frame, text='Valor minimo:').grid(row=1, column=0, pady=5)
        tk.Entry(frame, textvariable=self._valor_minimo).grid(row=1, column=1)
        tk.Label(frame, text='Valor maximo:').grid(row=2, column=0, pady=5)
        tk.Entry(frame, textvariable=self._valor_maximo).grid(row=2, column=1)
        tk.Button(self, text='Guardar cambios', command=self._evt_guardar_config).pack(pady=20)
        tk.Button(self, text='Regresar', command=self.evt_regresar).pack()

        self.evt_seleccionar_medicion(None)

    def evt_seleccionar_medicion(self, event):
        """
        Método de carga automática en memoria de los umbrales al seleccionar la medición.
        """
        tipo = self._tipo_medicion.get()
        dic_mediciones = {
            'Frecuencia Cardiaca': MedicionFrecuenciaCardiaca,
            'Temperatura': MedicionTemperatura,
            'Peso': MedicionPeso,            
            'Talla': MedicionTalla
        }
        clase = dic_mediciones[tipo]
        limites = self._gestor_umbrales.obtener_limites(clase)
        self._valor_minimo.set(limites.get('minimo', 0.0))
        self._valor_maximo.set(limites.get('maximo', 0.0))

    def _evt_guardar_config(self):
        """
        Método para guardar los valores de los límites de mediciones en el sistema.
        """
        try:
            tipo = self._tipo_medicion.get()
            minimo = self._valor_minimo.get()
            maximo = self._valor_maximo.get()
            dic_mediciones = {
                'Frecuencia Cardiaca': MedicionFrecuenciaCardiaca,
                'Temperatura': MedicionTemperatura,
                'Peso': MedicionPeso,
                'Talla': MedicionTalla
            }
            clase = dic_mediciones[tipo]
            self._gestor_umbrales.configurar_limites(clase, minimo, maximo)
            messagebox.showinfo('Éxito', 'Límites de mediciones guardados exitosamente.')
        except ValueError as ve:
            messagebox.showwarning("Validación", f'Datos Incorrectos: {ve}')
        except Exception as e:
            messagebox.showerror('Error. Está mal en algo.', str(e))
    
    def evt_regresar(self):
        """
        Método para regresar al menú principal.
        """
        self._controlador.mostrar_vista('VistaPacientes')