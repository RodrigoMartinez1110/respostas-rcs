import streamlit as st
import pandas as pd

st.title("Processador de Respostas RCS")

uploaded_files = st.file_uploader("Faça upload de um ou mais arquivos CSV", accept_multiple_files=True, type=["csv"])

def processar_arquivo(uploaded_file):
    # Criar DataFrame vazio para armazenar os dados processados
    base = pd.DataFrame()

    # Ler o arquivo em chunks
    chunk_size = 100_000  # Define um tamanho de chunk (ex: 100 mil linhas)
    for chunk in pd.read_csv(uploaded_file, sep=';', low_memory=False, chunksize=chunk_size, encoding='utf-8'):
        chunk = chunk.loc[chunk['STATUS'] == 'RESPONDIDO']
        
        # Lista de palavras para identificar bloqueios
        palavras_bloqueio = ['não sou', 'nao sou', 'sair', 'bloquear', 'pare', 
            'não quero', 'vai tomar no', 'foda-se', 'filho da puta', 'desinscrever',
            'remover', 'descadastrar', 'não me chame', 'não envie', 'não gosto', 'não conheço',
            'processo', 'denunciar', 'justiça', 'polícia', 'morreu', 'cancelar', 'cancela', 'obito']
        
        def categorizar_resposta(resposta):
            if pd.isna(resposta):
                return resposta
            resposta = resposta.lower().strip()
            for palavra in palavras_bloqueio:
                if palavra in resposta:
                    return "BLOQUEIO"
            return resposta
        
        # Categorizar as mensagens
        chunk['MENSAGEM'] = chunk['MENSAGEM'].apply(categorizar_resposta)
        
        # Adicionar o prefixo 55 e garantir que o número seja string
        chunk['NUMERO'] = chunk['NUMERO'].apply(lambda x: f"55{x}" if not str(x).startswith('55') else str(x))
        
        base = pd.concat([base, chunk])  # Concatena o chunk processado no DataFrame principal

    return base

if uploaded_files:
    lista = []
    for uploaded_file in uploaded_files:
        df_processado = processar_arquivo(uploaded_file)
        lista.append(df_processado)
    
    base = pd.concat(lista)
    
    # Selecionar bloqueados e responderam com o prefixo 55
    bloqueados = base.loc[base['MENSAGEM'] == 'BLOQUEIO', ['NUMERO']]
    responderam = base.loc[base['MENSAGEM'] != 'BLOQUEIO', ['NUMERO']]

    # Salvar em formato CSV como strings com o prefixo 55
    bloqueados_csv = bloqueados.to_csv(index=False, sep=';', header=['NUMERO'], encoding='utf-8').encode('utf-8')
    responderam_csv = responderam.to_csv(index=False, sep=';', header=['NUMERO'], encoding='utf-8').encode('utf-8')

    st.download_button("Baixar Lista de Bloqueados", bloqueados_csv, "bloqueados.csv", "text/csv")
    st.download_button("Baixar Lista de Responderam", responderam_csv, "responderam.csv", "text/csv")