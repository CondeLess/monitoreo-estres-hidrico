# 🌱 Dashboard IoT: Monitoreo de Estrés Hídrico en Vigna unguiculata

[![Streamlit App] : https://monitoreo-estres-hidrico-evc8fiwcmncam4s6scj8nb.streamlit.app

## 📌 Sobre el Proyecto
Esta aplicación web interactiva fue desarrollada para visualizar y analizar datos de humedad del suelo y temperatura ambiental capturados mediante un **microcontrolador ESP32**. El proyecto se centra en el monitoreo de ensayos agrícolas, específicamente en la evaluación del estrés hídrico en el cultivo de *Vigna unguiculata*.

El objetivo principal es proporcionar una herramienta remota y accesible para investigadores y agricultores, permitiendo la toma de decisiones basada en datos en tiempo real sin necesidad de conocimientos avanzados en programación.

## 🚀 Características Principales
* **Carga de Datos Personalizada:** Permite a los usuarios subir sus propios archivos `.csv` generados por sus sensores.
* **Métricas en Tiempo Real (KPIs):** Visualización rápida de los últimos valores registrados con indicadores de riesgo.
* **Análisis Temporal Interactivo:** Gráficos dinámicos (zoom, paneo, exportación) para comparar la evolución de la humedad entre el grupo control y el tratamiento de estrés.
* **Diseño Responsivo:** La interfaz se adapta si el set de datos incluye o no la variable de temperatura.
* **Exportación de Datos:** Acceso a la base de datos cruda directamente desde la web para auditorías o análisis externos.

## 🛠️ Tecnologías Utilizadas
* **Lenguaje:** Python 3
* **Framework Web:** Streamlit
* **Procesamiento de Datos:** Pandas, NumPy
* **Visualización:** Plotly Express

## 💻 Instalación y Uso Local
Si deseas correr este proyecto en tu propia máquina, sigue estos pasos:
  1. Clona este repositorio:
     git clone https://github.com/CondeLess/monitoreo-estres-hidrico.git
  2. Instala las dependencias necesarias:
     pip install -r requirements.txt
  4. Ejecuta la aplicación:
     streamlit run app.py

👨‍💻 Autor
Carlos D’Alessandro Condemarin Muñoz
Desarrollador IoT & Analista de Datos | Estudiante e Investigador

Liderando la integración de tecnología y ciencias agrícolas en el Círculo de Investigación en Agrotecnología (CIATEC).
