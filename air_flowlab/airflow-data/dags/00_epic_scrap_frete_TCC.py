
#------------ Bibliotecas para o Airflow-----------------

from airflow import DAG
from airflow.operators.python import PythonOperator, get_current_context
from airflow.utils.dates import days_ago
import logging

#------------Bibliotecas para o Web Scraping-------------
from datetime import datetime
from re import M
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
import numpy as np
import glob
import pytz

#____________Configuração do nível de Log___________
logging.basicConfig(format="%(name)s-%(levelname)s-%(asctime)s-%(message)s", level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

#_________Definição do proprietário do Job e número de tentativas__________
default_args = {
    'owner': 'admin',
    'retries':1,
 }

#_____________Parâmetros da DAG_____________
dag = DAG(
    '00_epic_tcc_ETL_fretes',
    default_args=default_args,
    description='DAG para extração de dados de Frete',
    schedule_interval='@daily',
    start_date=days_ago(1),
    tags=['TCC','Fretes', 'PUC_Minas'],
) 

#_______________Dag da Extração_____________
def extract_data (**kwargs):
    class p1:
        headers = {'User-Agent': 'My User Agent 1.0','From': 'youremail@domain.com' }
        link = requests.get('https://www.truckpad.com.br/fretes/',headers=headers).content
        soup = BeautifulSoup(link, features="lxml")
        link = [div.find('a')['href']
        for div in soup.find_all('div', 'freight-card-buttons')]
        #Aqui denfine o numero de páginas, no desenvolvimento optou-se pelo número 20 Retorna qtd páginas
        val_results = 438 #int(soup.find('h2','count-results').get_text().split(' ')[0])/len(link)
        valor, veiculo, carroceria, peso, natureza, tipo, km, adiantamento, origem, destino, ton = [], [], [], [], [], [], [], [], [], [], []
    def extracao(data):
        fim = False
        kwargs['ti'].xcom_push(key='Fim', value=fim)
        i = data
        if i != 1:
            url = requests.get(
                'https://www.truckpad.com.br/fretes/?pagina='+str(i), headers=p1.headers).content
            soup1 = BeautifulSoup(url, features="lxml")
            p1.link = [div.find('a')['href'] for div in soup1.find_all(
                'div', 'freight-card-buttons')]
        for i in p1.link:
            soup2 = BeautifulSoup(requests.get(
                'https://www.truckpad.com.br'+i, headers=p1.headers).content, "lxml")
            try: 
                val = soup2.find('div','details-payment').find_all('strong')[0].get_text()
            except:
                val=np.nan
            p1.valor.append(val)
            p1.ton.append(soup2.find('strong',"information-per-ton").get_text())
            f_veic = [li.get_text() for li in soup2.find('div','details-content').find('ul').find_all('li')]
            f_carroce = [li.get_text() for li in soup2.find('div','details-content').find_all('ul')[1].find_all('li')]
            p1.veiculo.append(f_veic)
            p1.carroceria.append(f_carroce)
            p1.peso.append(soup2.find('div','details-truckload').find_all('strong')[3].get_text())
            p1.natureza.append(soup2.find('div','details-truckload').find_all('strong')[5].get_text())
            p1.tipo.append(soup2.find('div','details-truckload').find_all('strong')[2].get_text())
            p1.km.append(soup2.find('p','information information--icon-distance information-distance').find('strong').get_text())
            p1.origem.append(soup2.find('div','route').find('strong').get_text())
            p1.destino.append(soup2.find('div','route').find_all('strong')[1].get_text())
            p1.adiantamento.append(soup2.find('div','details-payment').find_all('strong')[2].get_text())
    logger.info('=============Inicio da Extração=============')
    for i in range(1, int (p1.val_results+1)):
        print (i, end = ':')
        try:
            extracao(i)     
        except:
            try:
                extracao(i)
            except:
                continue
        finally:
            if i == p1.val_results:
                df_exp = pd.DataFrame(list(zip(p1.destino, p1.origem, p1.km, p1.valor, p1.ton, p1.natureza, p1.tipo, p1.veiculo)))
                df_exp.columns = ['destino', 'origem', 'km', 'valor', 'ton', 'natureza', 'tipo', 'veiculo']
                #para ocupar menos espaço está em gzip, portável para HDFS.
                df_exp.to_csv('/home/airflow/files/fretes/extract.gzip', sep=';' , encoding='utf-8', compression='gzip')
                fim = True 
                kwargs['ti'].xcom_push(key='Fim', value=fim)
                logger.info('=============Extração Finalizada em %i paginas=============',i)
            

#________________DAG da transformação, retira-se caracteres epeciais_______________
def transform_data(**kwargs):
    uf_destino, uf_origem, cidade_origem, cidade_destino, pkm, ped, pton, preco, produto, especie, veic_1, veic_2 = [], [], [], [], [], [], [], [], [], [], [], []
    ti = kwargs['ti']
    Fim = ti.xcom_pull(key='Fim', task_ids=['extract_datal'])
    if Fim == False: 
        kwargs['ti'].xcom_push(key='Fim', value=fim)
        return kwargs['message'] 
    logger.info('=============Inicio da Trasformação=============')
    df_imp = pd.read_csv('/home/airflow/files/fretes/extract.gzip', sep=';' , encoding='utf-8', compression='gzip')
    df_imp['ton'].fillna("", inplace=True)
    destino, origem, valor, km, ton, natureza, tipo, veiculo = df_imp['destino'],df_imp['origem'],df_imp['valor'],df_imp['km'],df_imp['ton'], df_imp['natureza'],df_imp['tipo'],df_imp['veiculo']
    veiculo = df_imp['veiculo'].values.tolist()
    veiculo = [ind.strip('][').split(', ') for ind in veiculo]
    uf_destino = [re.search(r'(.*?)-',val).group(1).strip() for val in destino]
    uf_origem = [re.search(r'(.*?)-',val).group(1).strip() for val in origem]
    cidade_origem = [re.search(r'-(.*?)$',val).group(1).strip() for val in origem]
    cidade_destino = [re.search(r'-(.*?)$',val).group(1).strip() for val in destino]
    pkm = [int(val.replace('Km','')) if 'Km' in val else val for val in km]
    ped = [1 if "Pedágio" in val else 0 for val in valor]
    pton = [1 if 'tonelada' in val else 0 for val in ton]
    for val in valor:
        if 'combinar' in val.lower():
            preco.append(np.nan)
        else:
            preco.append(re.search(r'R\$(.*?)($|\+)',val).group(1))
    produto = natureza
    especie = tipo
    for nveic in veiculo:
        if len(nveic)<2:
            veic_1.append(nveic[0])
            veic_2.append(np.nan)
        else:
            veic_1.append(nveic[0])
            veic_2.append(nveic[1])
    df_tnf = pd.DataFrame(list(zip(uf_destino, uf_origem, cidade_origem, cidade_destino, pkm, ped, pton, preco, produto, especie, veic_1, veic_2)))
    df_tnf.columns = ['UF_Destino', 'UF_origem', 'Origem', 'Destino', 'KM', 'PED', 'Pton', 'Preco', 'Produto', 'Especie', 'Veiculo_1', 'Veiculo_2']
    df_tnf.to_csv('/home/airflow/files/fretes/transform.gzip', sep=';' , encoding='utf-8', compression='gzip')
    logger.info('=============Fim da Trasformação=============')


#_________________Nessa DAG faz o salvamento do arquivo final, podendo ser para um banco, nesse caso será em disco. 
def load_data(**kwargs):
    logger.info('=============Salva os dados em Excel=============')    
    df_load = pd.read_csv('/home/airflow/files/fretes/transform.gzip', sep=';' , encoding='utf-8', compression='gzip')
    #limpesza final \w tudo que for letra e numero
    for column in df_load.columns:
        df_load[column] = df_load[column].replace([r'\w\$.,-/ \(\)'], '')
    df_load.drop([0, 1])    
    df_load['Ano']=datetime.now(pytz.timezone('Brazil/East')).timetuple()[0]
    df_load['Mes']=datetime.now(pytz.timezone('Brazil/East')).timetuple()[1]
    df_load['Dia']=datetime.now(pytz.timezone('Brazil/East')).timetuple()[2]
    agora = datetime.now(pytz.timezone('Brazil/East'))
    path = "/home/airflow/files/fretes/"
    all_files = glob.glob(path + "/*.csv")
    d1 = agora.strftime("%Y%m%d_%H%M")+'.csv'
    d3 = r'{}\{}'.format(path, d1)
    colunas = ["UF_Destino","UF_origem","Origem", "Destino","KM",
            "PED","Pton","Preco","Produto","Especie","Veiculo_1",
            "Veiculo_2","Ano","Mes","Dia"
    ]
    if d3 in all_files:
        d2 = agora.strftime("%Y%m%d_%H%M")+'_1.csv'
        df_load[colunas].to_csv(path+d2, sep=';' , encoding='utf-8')
    else:
        df_load[colunas].to_csv(path+d1, sep=';' , encoding='utf-8')
    return kwargs['message'] 

#________Parâmetros e sequenciamento da ETL em DAG's____________
extrai_dados = PythonOperator(task_id="extrai_dados",
                              python_callable=extract_data,
                              provide_context=True,dag=dag,)

transforma_dados = PythonOperator(task_id="transforma_dados",
                                python_callable=transform_data,
                                provide_context=True,
                                op_kwargs={'message': 'Transforamação interrompida'},dag=dag,)

salva_dados = PythonOperator(task_id="salva_dados",
                            python_callable=load_data,
                            provide_context=True,
                            op_kwargs={'message': 'Fim do Scrap automatizado'},dag=dag,)

extrai_dados >> transforma_dados >> salva_dados

##Pode instalar diretamente no airflow os requirements ou utiliza vitualenv.

#  [START howto_operator_python_venv]
#def callable_virtualenv():
#    for _ in range(2):
#        print('Por favor aguarde...', flush=True)
#    print('fim')
#    import glob
#    from bs4 import BeautifulSoup
#
#
#virtualenv_task = PythonVirtualenvOperator(
#    task_id="virtualenv_python",
#    python_callable=callable_virtualenv,
#    requirements=[
#        "beautifulsoup4==4.9.3",
#        "bs4==0.0.1",
#        "lxml==4.6.1",
#        "openpyxl==3.0.5"
#    ],
#    system_site_packages=False,
#    dag=dag,
#)
#virtualenv_task >> 

#extrai_dados >> transforma_dados >> salva_dados
