# TCC PucMinas -  Stanley Cruvinel :coffee:
## Pós-graduação Lato Sensu em Ciência de Dados e Big Data
**Conteúdo** 

<!-- toc -->

- [air_flowlab]
  - ./air_flowlab/docker-compose.yml
  - ./air_flowlab/airflow-data/dags (DAG e requirements.txt)
  - ./air_flowlab/airflow-data/files/fretes (Dados de fretes,  01/02/2021)
- [spark_jupyterlab]
  - ./spark_jupyterlab/docker-compose.yml
  - ./spark_jupyterlab/.env
  - ./data/view/tcc_pucminas_cidades.html 
  - ./data/view/pucminas_tcc_fretesuf.html
  - ./data/01_TCC_PUCMinas_StanleyCruvinel.ipynb
  - ./data/02_TCC_PUCMinas_StanleyCruvinel_ML.ipynb
  - ./data/fretes.csv

<!-- tocstop -->

## Criando os ambientes
- Requer instalação do Docker Desktop. 

```console
$ git clone https://github.com/StanleyCruvinel/tcc_ml_puc
$ cd tcc_ml_puc/air_flowlab
```

### air_flowlab

```console
$ docker compose -p p2 up --build -d postgres redis
$ docker compose -p p2 up --build -d initdb user
$ docker compose -p p2 up --build -d
$ docker exec -it airflow_scheduler bash
    >pip install -r dags/requirements.txt
    >exit
$ docker exec -it airflow_worker1 bash
    >pip install -r dags/requirements.txt
    >exit
$ docker ps --format "{{.Names}}"
$ docker rm initdb createuser
```
http://localhost:8088 
admin:admin

### spark_jupyterlab

```console
$ cd ../spark_jupyterlab
$ docker-compose -p p2 up --build -d 
```
# Jupyter Lab
http://localhost:8888/

**UI Spark**
http://localhost:4040
  **Master**
     http://localhost:8080
  **Worker1**
    http://localhost:8081
  **Worker2**
    http://localhost:8082

No notebook 01_TCC_PUCMinas_StanleyCruvinel.ipynb instale as bibliotecas.

```
!pip install networkx pyvis pandas
```


### se precisar de UI para visualizar o ambiente.

```console
$ docker run -d -p 9002:9000 --name=portainer -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data  portainer/portainer-ce:2.1.1-alpine
```

http://localhost:9002
