# tcc pucMinas Stanley Cruvinel


**Conteúdo** :coffee 

<!-- toc -->

- [air_flowlab]#air_flowlab
  - ./air_flowlab/docker-compose.yml
  - ./air_flowlab/airflow-data/dags (DAG e requirements.txt)
  - ./air_flowlab/airflow-data/files/fretes (Dados de fretes,  01/02/2021)
- [spark_jupyterlab]#spark_jupyterlab
  - ./spark_jupyterlab/docker-compose.yml
  - ./spark_jupyterlab/.env
  - ./data/view/tcc_pucminas_cidades.html 
  - ./data/view/pucminas_tcc_fretesuf.html
  - ./data/01_TCC_PUCMinas_StanleyCruvinel.ipynb
  - ./data/02_TCC_PUCMinas_StanleyCruvinel_ML.ipynb
  - ./data/fretes.csv

<!-- tocstop -->

## Criando os ambientes
- Necessário o Docker Desktop instalado. 

### air_flowlab

```console
$ docker-compose -p p2 up --build -d postgres redis
$ docker-compose -p p2 up --build -d initdb user
$ docker-compose -p p2 up --build -d airflow airflow-scheduler airflow-worker1 airflow-flower
$ docker exec -it airflow_worker1 bash
    >cd dags
    >pip install -r requirements.txt
$ docker exec -it airflow bash
    >cd dags
    >pip install -r requirements.txt
$ docker ps --format "{{.Names}}"
$ docker rm initdb user
```
http://localhost:8080 


### spark_jupyterlab

```console
$ docker-compose -p p2 up --build -d 
```

http://localhost:8888/

### se precisar de UI para visualizar o ambiente.

```console
$ docker run -d -p 9002:9000 --name=portainer -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data  portainer/portainer-ce:2.0.0-alpine
```

http://localhost:9002