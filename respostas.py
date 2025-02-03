import streamlit as st
import pandas as pd
import unicodedata

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
        palavras_bloqueio = [
            'não sou', 'nao sou', 'sair', 'bloquear', 'pare', 
            'não quero', 'vai tomar no', 'foda-se', 'filho da puta', 'desinscrever', 
            'remover', 'descadastrar', 'não me chame', 'não envie', 'não gosto', 'não conheço',
            'eu nao sou', 'eu n sou', 'n sou', 'processo', 'processar', 'proceso', 'denunciar', 
            'descadastr', 'nao sei quem', 'incomoda', 'bloqueio', 'bloqueiar', 'block', 'engano', 
            'nao é', 'não é', 'voce poderia me fazer um grande favor', 'nao me chamo', 
            'can you help me out?', 'caralho', 'krl', 'kct', 'cacete', 'porra', 'fdp', 'desgraca', 
            'buceta', 'poha', 'filha da puta', 'filho da puta', 'fodase', 'foda', 'fds', 'puta', 
            'viado', 'cu', 'nao sei que', 'nao sei quem e', 'não conheço', 'nao conheco', 
            'merda', '190', 'tmnc', 'para de mandar', 'nao param de mandar mensagem', 
            'nome nao e', 'vai tomar n', 'esse numero nao e', 'não é o celular', 'nao sou',
            'me esquece', 'judicial', 'numero nao pertence', 'nao e de', 
            'mensagem para a pessoa errada', 'nao pertence', 'nunca foi', 
            'morreu', 'obito', 'telefone nao e', 'nao existe', 'nao tem ninguem', 
            'pessoa errada', 'nao tem nenhum', 'cancelar', 'cancela', 'n pertence', 
            'nao. sou.', 'mandando errado', 'exclui esse numero', 'nao quero receber mais', 'puta que pariu', 'pariu', 'puta', 'não tenho contato',
            'não mandar mais', 'nao mandar mais', 'esse celular não é', 'encher o saco', 'vai se fuder', 'vsf', 'se fude', 'não quero recebe', 'justiça', 'policia', 'polícia',
            'denunciar', 'justiça   ', 'justiça', 'meu pau', 'minha pica', 'pika', 'não tem nenhum', 'nao me encha', 'Não sou'
        ]

        def normalizar_texto(texto):
            # Remove caracteres especiais e normaliza o texto
            return ''.join(
                c for c in unicodedata.normalize('NFD', texto)
                if unicodedata.category(c) != 'Mn'
            )
        
        def categorizar_resposta(resposta):
            # Normaliza e converte para minúsculas
            resposta = normalizar_texto(resposta.lower().strip())
            
            for palavra in palavras_bloqueio:
                palavra_normalizada = normalizar_texto(palavra)
                if palavra_normalizada in resposta:
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
    
    bloqueados = base.loc[base['MENSAGEM'] == 'BLOQUEIO', ['NUMERO']].astype(str).drop_duplicates()
    responderam = base.loc[base['MENSAGEM'] != 'BLOQUEIO', ['NUMERO']].astype(str).drop_duplicates()

    # Salvar em formato CSV como strings com o prefixo 55
    bloqueados_csv = bloqueados.to_csv(index=False, sep=';', header=['NUMERO'], encoding='utf-8').encode('utf-8')
    responderam_csv = responderam.to_csv(index=False, sep=';', header=['NUMERO'], encoding='utf-8').encode('utf-8')

    st.download_button("Baixar Lista de Bloqueados", bloqueados_csv, "bloqueados.csv", "text/csv")
    st.download_button("Baixar Lista de Responderam", responderam_csv, "responderam.csv", "text/csv")
