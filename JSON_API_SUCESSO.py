



from flask import Flask
from flask import jsonify
import pandas as pd
import requests
from datetime import date, time, datetime, timedelta
from dateutil.relativedelta import relativedelta
from math import radians, cos, sin, asin, sqrt
import json

app = Flask(__name__)
@app.route("/buscar/<string:ida>/<string:volta>/<string:data_saida>/<string:data_volta>", methods=["GET"])
def buscar(ida,volta,data_saida,data_volta):
  local_ida = ida
  local_volta = volta
  data1 = data_saida
  data2 =data_volta

  
### FUNÇÃO QUE TEM COMO OBJETIVO REALIZAR A BUSCA NA API DE TERCEIROS ###
  
  def busca_completa(destino_origem,destino_final,data_ida,data_volta):
      
### FUNÇÃO QUE TEM POR OBJETIVO VALIDAR E TRATAR OS DADOS DE DATA ###
      
      
    def valida_destino(data_chegada , data_partida):

      hora_str_chegada = str(data_chegada)
      hora_chegada= datetime.strptime(hora_str_chegada, "%Y-%m-%d")
      hora_str_partida= str(data_partida)
      hora_partida= datetime.strptime(hora_str_partida, "%Y-%m-%d")
      tempo_voo = str(hora_chegada - hora_partida)
      return tempo_voo

### FUNÇÃO QUE TEM COMO OBJETIVO CALCULAR A VELOCIDADE DA VIAGEM ###

    def velocidade_voo(data_chegada , data_partida,distancia):
          hora_str_chegada = str(data_chegada)
          hora_str_chegada= hora_str_chegada.replace('T',' ')
          hora_chegada= datetime.strptime(hora_str_chegada, "%Y-%m-%d %H:%M:%S")
          hora_str_partida= str(data_partida)
          hora_str_partida= hora_str_partida.replace('T',' ')
          hora_partida= datetime.strptime(hora_str_partida, "%Y-%m-%d %H:%M:%S")
          tempo_voo = str(hora_chegada - hora_partida)
          valores_conv = tempo_voo.split(':')
          tempo_gasto = round(int(valores_conv[0])+(int(valores_conv[1])/60)+((int(valores_conv[2]))/60)/60,2)
          velocidade = round(distancia/tempo_gasto,2)
          return velocidade
      
### FUNÇÃO QUE TEM COMO OBJETIVO CALCULAR A DISTANCIA UTILIZANDO A LAT E LONG ###
      
    def haversine(lon1, lat1, lon2, lat2):
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        r = 6371 # Radius of earth in kilometers. Use 3956 for miles
        return c * r
    
#### FUNÇÃO QUE TEM COMO OBJETIVO REALIZAR TANTO A BUSCA DE IDA E BUSCA DE VOLTA DA VIAGEM ####

    def busca_voos(iata_partida,iata_chegada,data_viagem):
        chave_key ='qEbvlDxInweeAIjmOzEl9vKKKMrdkvLV'
        url = f'http://stub.2xt.com.br/air/search/{chave_key}/{iata_partida}/{iata_chegada}/{data_viagem}'
        res = requests.get(url, auth=('test','tB7vlD'))
        res = res.text
        dados_json = json.loads(res)
        resumo = dados_json['summary']
        dados_opcoes = dados_json["options"]
        df_resumo = pd.DataFrame(data=resumo)
        pd.set_option('display.max_columns', None) # fazer retirada de linha pois nao intefdre / apenas visualização 
        data_inicial = []
        data_final = []
        taxa_passagem = []
        taxa_fee = []
        modelo = []
        fabricante = []
        trajeto = []
        velocidade_trajeto = []
        custo_por_km = []
        total_valor = []
        for i in range(len(dados_opcoes)):
          df_opcoes = pd.DataFrame(data=dados_opcoes[i])
          df_opcoes.rename(columns={'departure_time': 'HORARIO_PARTIDA','arrival_time':'HORARIO_CHEGADA','price':'PREÇO','aircraft':'AERONAVE','meta':'META'},inplace = True)
          df_opcoes['PREÇO'][1] = (df_opcoes.iloc[0][2])*0.1
          df_opcoes['PREÇO'][2]= df_opcoes['PREÇO'][0]+ df_opcoes['PREÇO'][1]
          df_opcoes['META'][5] = round(haversine(df_resumo['from'][3],df_resumo['from'][2],df_resumo['to'][3],df_resumo['to'][2]),2)
          df_opcoes['META'][6] = velocidade_voo(df_opcoes['HORARIO_CHEGADA'][0],df_opcoes['HORARIO_PARTIDA'][0],df_opcoes['META'][5])
          df_opcoes['META'][7] = round(df_opcoes.iloc[0][2]/df_opcoes['META'][5] ,2)
          data_inicial.append(df_opcoes['HORARIO_PARTIDA'][0]),data_final.append(df_opcoes['HORARIO_CHEGADA'][0]),taxa_passagem.append(df_opcoes.iloc[0][2])
          taxa_fee.append(df_opcoes['PREÇO'][1]),modelo.append(df_opcoes['AERONAVE'][3]), fabricante.append(df_opcoes['AERONAVE'][4]),trajeto.append(df_opcoes['META'][5])
          velocidade_trajeto.append(df_opcoes['META'][6]), custo_por_km.append(df_opcoes['META'][7]), total_valor.append(df_opcoes['PREÇO'][2])
        tabela = {'HORARIO_PARTIDA':data_inicial,'HORARIO_CHEGADA':data_final,'MODELO':modelo ,'FABRICANTE':fabricante,
                  'DISTANCIA (KM)':trajeto ,'VELOCIDADE (KM/H)':velocidade_trajeto,'CUSTO/KM':custo_por_km,'PASSAGEM':taxa_passagem,'TAXA_SERVIÇO':taxa_fee,
                  'TOTAL - (R$)':total_valor}
        opcoes_pass = pd.DataFrame(data=tabela)
        return opcoes_pass
      
    if str(destino_origem) != str(destino_final) :
      valida_data_final = str(valida_destino(data_volta,data_ida))
      valida_data_final = valida_data_final.split(' ')
      if len(valida_data_final)!= 1:
        valida_data_final = int(valida_data_final[0])
      else:
        valida_data_final = 0
      if valida_data_final != 0 and valida_data_final > 0 :  
        opcoes_de_ida = busca_voos(destino_origem,destino_final,data_ida)
        opcoes_de_volta = busca_voos(destino_final,destino_origem,data_volta)
        return opcoes_de_ida ,opcoes_de_volta
      else :
        print('VERIFIQUE OS DADOS DE ENTRADA, POIS AS DATAS NÃO PODEM SER IGUAIS !')
        return str('F'),str('F')
    else :
      print('VERIFIQUE OS DADOS DE ENTRADA, POIS OS DESTINOS NÃO PODEM SER IGUAIS.')
      return str('F'),str('F')

### FUNÇÃO QUE REALIZA A COMBINAÇÃO E POSSIBILIDADES DE VOOS OFERECIDOS ###

  def combina_voos(x ,y):
    data_ida_volta= []
    modelo_ida_volta = []
    fabricante_ida_volta = []
    distancia_ida_volta =[]
    velocidade_ida_volta = []
    custo_ida_volta = []
    passagem_ida_volta =[]
    taxa_ida_volta = []
    total_ida_volta = []

    for i in range(len(x.index)):
      data_1 = x['HORARIO_PARTIDA'][i]
      modelo_1 = x['MODELO'][i]
      fabri_1 = x['FABRICANTE'][i]
      distan_1 = x['DISTANCIA (KM)'][i]
      veloc_1 = x['VELOCIDADE (KM/H)'][i]
      custo_1 = x['CUSTO/KM'][i]
      pass_1 = x['PASSAGEM'][i]
      taxa_1 = round(x['TAXA_SERVIÇO'][i],2)
      valor_1 = x['TOTAL - (R$)'][i]
      for k in range(len(y.index)):
        data_2 = y['HORARIO_PARTIDA'][k]
        modelo_2 = y['MODELO'][k]
        fabri_2 = y['FABRICANTE'][k]
        distan_2 =y['DISTANCIA (KM)'][k]
        veloc_2 = y['VELOCIDADE (KM/H)'][k]
        custo_2 = y['CUSTO/KM'][k]
        pass_2 = y['PASSAGEM'][k]
        taxa_2 = round(y['TAXA_SERVIÇO'][k],2)
        valor_2 = y['TOTAL - (R$)'][k]
        data_ida_volta.append(f'{data_1} - {data_2}'),modelo_ida_volta.append(f'{modelo_1} - {modelo_2}'), fabricante_ida_volta.append(f'{fabri_1} - {fabri_2}'),
        distancia_ida_volta.append(f'{distan_1} - {distan_2}'),velocidade_ida_volta.append(f'{veloc_1} - {veloc_2}'),  custo_ida_volta.append(f'{custo_1} - {custo_2}'),
        passagem_ida_volta.append(f'{pass_1} - {pass_2}'), taxa_ida_volta.append(f'{taxa_1} - {taxa_2}'), total_ida_volta.append(round(valor_1 + valor_2,2)) 

    dic_valores = {'DATA: IDA/VOLTA':data_ida_volta,'MODELO: IDA/VOLTA':modelo_ida_volta,
                          'FABRICANTE: IDA/VOLTA':fabricante_ida_volta,'DISTANCIA: IDA/VOLTA':distancia_ida_volta,
                          'VELOCIDADE: IDA/VOLTA':velocidade_ida_volta,'CUSTO-KM: IDA/VOLTA':custo_ida_volta,
                          'PASSAGEM: IDA/VOLTA':passagem_ida_volta,'TAXA-SERV: IDA/VOLTA':taxa_ida_volta,
                          'TOTAL':total_ida_volta}
    dados_comb = pd.DataFrame(data=dic_valores)
    dados_comb = dados_comb.sort_values(by=['TOTAL'])
    return dados_comb
    

  ### FUNÇÃO QUE TEM COMO OBJETIVO VALIDAR SE O AEROPORTO ESTA NA BASE DE DADOS ###

  def valida(aero_1,aero_2):

    url = f'http://stub.2xt.com.br/air/airports/qEbvlDxInweeAIjmOzEl9vKKKMrdkvLV'
    res = requests.get(url, auth=('test','tB7vlD'))
    res = res.text
    obj = json.loads(res)
    if (aero_1 in obj)  :
      return True
    if str(aero_1) == str(aero_2):
      return False

   
  dado_inicio = local_ida.upper()
  dado_final = local_volta.upper()
  data_de_ida = data1.upper()
  data_de_volta = data2.upper()
  valida_1 = valida(dado_inicio,dado_final)


  if valida_1 and len(data_de_ida)==10 and len(data_de_volta)==10 and str(dado_inicio) != str( dado_final) :

    dados_1,dados_2 = busca_completa(dado_inicio,dado_final,data_de_ida,data_de_volta)

    if type(dados_1)!= str:
      
      voos_combinados = combina_voos(dados_1,dados_2)
      js = voos_combinados.to_json(orient = 'columns')
      response = app.response_class(
        response=js,
        status=200,
        mimetype='application/json')
      return response

  else:
    if (valida_1 == False) or dado_inicio == dado_final  :
      return ('AEROPORTO INDISPONIVEL PARA CONSULTA / ACRONIMOS INVALIDOS DEVE SEGUIR O PADRÃO (ABC) / AEROPORTOS NÃO PODEM SER IGUAIS',404)
    else :
      return ('DATA INVALIDA : VOCÊ DEVE SEGUIR PADRÃO (AAAA-MM-DD) ',409)
  if data_de_ida == data_de_volta  :
    return ('ATENÇÃO : DATA DE IDA E IGUAL A DATA DE VOLTA',409)

     

app.run(host='0.0.0.0')
  


  






  




