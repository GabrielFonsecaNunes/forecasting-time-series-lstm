import pandas as pd
from binance.client import Client
import plotly.graph_objects as go
from hyperopt import fmin, hp, tpe

api_key = "A6X3Bl8R7rZweC5eSOT0It3JXrDZwbDmVhmSEty6BEjXKTOk1kQIbC605jqvkoj2"
api_secret = "ovF6YXVbZsICLLx91jFeBX6kUknHa6j7K3J2ADxE1438WGEre9o5Ca1fIoX03ngI"

client = Client(api_key= api_key, api_secret=api_secret)

symbol = 'BTCUSDT'
interval = '1h'
limit = 24 * 30

klines = client.futures_klines(symbol=symbol, interval=interval, limit=limit)

data = []
for kline in klines:
    timestamp = pd.to_datetime(kline[0], unit='ms')
    open_price = float(kline[1])
    high_price = float(kline[2])
    low_price = float(kline[3])
    close_price = float(kline[4])
    volume = float(kline[5])

    data.append([timestamp, open_price, high_price, low_price, close_price, volume])

df = pd.DataFrame(data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])

def simular(df, media_movel, num_std):
    """
    """
    df['MA'] = df['Close'].rolling(window= int(media_movel)).mean()
    df['STD'] = df['Close'].rolling(window= int(media_movel)).std()
    df['Upper'] = df['MA'] + num_std * df['STD']
    df['Lower'] = df['MA'] - num_std * df['STD']

    capital = 250
    capital_op = capital
    quantidade_moeda = 0

    operacoes_dict = {
        'capital': [],
        'qtde_moeda': [],
        'qtde_moeda_operacao': [],
        'valor': [],
        'tp_operacao': [],
        'lucro': [],
        'date': []
    }

    operacoes_df = pd.DataFrame(data= operacoes_dict)

    for index, row in df.iterrows():

        quantidade_moeda_compra = 0.002
        quantidade_moeda_venda = 0.004

        # Comprar a moeda
        if row['Close'] < row['Lower'] and capital >= row['Close'] * quantidade_moeda_compra * (1.001) and quantidade_moeda <= 0.001:

            # Capital antes operacao
            capital_inicial = capital

            # Valor compra USD
            valor_compra = row['Close'] * quantidade_moeda_compra

            # Taxa Operacao USDT
            taxa_operacao = valor_compra * 0.001

            # Compra moeda carteira
            quantidade_moeda += quantidade_moeda_compra

            # Valor final
            valor_final = valor_compra * 1.001

            capital -= valor_final

            #Lucro
            lucro = capital - capital_inicial

            operacoes_df.loc[len(operacoes_df)] =   {
                                                        'capital': capital, 
                                                        'qtde_moeda': quantidade_moeda, 
                                                        'qtde_moeda_operacao' : quantidade_moeda_compra, 
                                                        'valor': valor_final,
                                                        'tp_operacao': 'Compra',
                                                        'lucro': lucro,
                                                        'date': row['Timestamp']
                                                    }
        
        # Vender a moeda
        elif row['Close'] > row['Upper'] and quantidade_moeda >= quantidade_moeda_venda:

            # Capital antes operacao
            capital_inicial = capital

            # Retirada moeda carteira
            quantidade_moeda -= quantidade_moeda

            # Valor venda USD
            valor_venda = row['Close'] * quantidade_moeda_venda

            # Taxa Operacao USDT
            taxa_operacao = valor_venda * 0.001
            
            valor_final = valor_venda - taxa_operacao

            capital += valor_final
            lucro = capital - capital_inicial

            operacoes_df.loc[len(operacoes_df)] =   {
                                                        'capital': capital, 
                                                        'qtde_moeda': quantidade_moeda, 
                                                        'qtde_moeda_operacao' : quantidade_moeda_venda, 
                                                        'valor': valor_final,
                                                        'tp_operacao': 'Venda',
                                                        'lucro': lucro,
                                                        'date': row['Timestamp']
                                                    }

    lucro_op = capital_op - capital

    return lucro_op

# Função para otimização
def otimizar(params):
    # Extrair os parâmetros
    media_movel = params['media_movel']
    desvio_padrao = params['desvio_padrao']
    
    # Realizar cálculos e simulações com os parâmetros
    # Supondo que você tenha uma função chamada 'simular' que recebe
    # a média móvel e o desvio padrão como argumentos e retorna o lucro
    
    lucro = simular(df, media_movel, desvio_padrao)
    
    return -lucro  # Objetivo é maximizar o lucro, então invertemos o sinal


# Espaço de busca dos parâmetros
espaco_busca = {
    'media_movel': hp.quniform('media_movel', 5, 60, 5),
    'desvio_padrao': hp.quniform('desvio_padrao', 2, 3.5, 0.01)
}

# Otimização com Hyperopt
melhores_parametros = fmin(otimizar, espaco_busca, algo=tpe.suggest, max_evals=200)

print('Melhores parâmetros encontrados:')
print(melhores_parametros)