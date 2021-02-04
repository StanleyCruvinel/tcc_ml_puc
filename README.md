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
$ docker-compose -p p2 up --build -d postgres redis
$ docker-compose -p p2 up --build -d initdb user
$ docker-compose -p p2 up --build -d
$ docker exec -it airflow_scheduler bash
    >pip install -r dags/requirements.txt
$ docker exec -it airflow_worker1 bash
    >pip install -r dags/requirements.txt
$ docker ps --format "{{.Names}}"
$ docker rm initdb createuser
```
http://localhost:8080 
admin:admin

### spark_jupyterlab

```console
$ cd ../spark_jupyterlab
$ docker-compose -p p2 up --build -d 
```

http://localhost:8888/

Para o notebook 01_TCC_PUCMinas_StanleyCruvinel.ipynb instalar as bibliotecas em uma nova célula.

```
!pip install networkx pyvis pandas
```


### se precisar de UI para visualizar o ambiente.

```console
$ docker run -d -p 9002:9000 --name=portainer -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data  portainer/portainer-ce:2.0.0-alpine
```

http://localhost:9002
