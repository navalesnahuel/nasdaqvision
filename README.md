
<p align="center">
<img height="200" width="200" src="img/nasdaq-grey.png"/>
</p>
<h1 align="center">Nasdaq Vision</h1>

## Descripcion
<p>Este repositorio contiene un proyecto personal</p>
<p>Se centra en el desarrollo de una pipeline que extrae, transforma y carga datos desde y hacia diversas fuentes.</p>
<p>Además, incluye la creación de un dashboard con visualizaciones utilizando Streamlit.</p>

---
## Infraestructura
### Herramientas y Servicios
![spark](https://img.shields.io/badge/Apache_Spark-FF694B?style=flat-square&logo=apache-spark&logoColor=white) ![streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white) ![airflow](https://img.shields.io/badge/Apache_Airflow-844FBA?style=flat-square&logo=apache-airflow&logoColor=white) ![docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white) ![minio](https://img.shields.io/badge/MinIO-ff4b4b?style=flat-square&logo=minio&logoColor=white) ![postgres](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white) 

---
## Diagrama del Pipeline

![Diagrama del Pipeline](img/diagram.png)

---

## Data Pipeline

#### ETL Orquestado y automatizado con [Airflow](https://airflow.apache.org/)
- Extracción [NASDAQ](https://www.nasdaq.com/): Obtiene datos base de símbolos bursátiles
- Extracción Histórica: Obtiene información histórica de cada símbolo usando la API de [YFinance](https://finance.yahoo.com/)
- Procesamiento: Limpia y carga los datos en nuestro Datawarehouse

#### Visualización con [Streamlit](https://streamlit.io/)
- Dashboard conectado a nuestra base [PostgreSQL](https://www.postgresql.org/)
- Integración con [NewsAPI](https://newsapi.org/)
- Visualización de datos históricos, noticias y mas.

---
