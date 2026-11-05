FROM apache/airflow:3.3.2-python3.12

COPY --chown=airflow:root pyproject.toml README.md /opt/projet/
COPY --chown=airflow:root src /opt/projet/src
RUN pip install --no-cache-dir "apache-airflow==3.3.2" /opt/projet