import streamlit as st
from pymongo import MongoClient
from bson import ObjectId
import pandas as pd

# Configuração da conexão com o MongoDB
client = MongoClient('mongodb+srv://bni:bY480rj1F32SH59M@db-mongodb-nyc3-40847-b8cad3fe.mongo.ondigitalocean.com/convidados?tls=true&authSource=admin&replicaSet=db-mongodb-nyc3-40847')
db = client.evento_db
collection = db.convidados


# Função para obter dados do MongoDB com a opção de filtro por nome
def get_data(name_filter=None):
    query = {"nome": {"$regex": name_filter, "$options": "i"}} if name_filter else {}
    return list(collection.find(query))

# Função para atualizar o status 'presente' e 'recebeu kit'
def update_status(name, field, new_value):
    collection.update_one({"name": name}, {"$set": {field: new_value}})

# Função para renderizar a tabela no dashboard com busca e paginação
def render_table():
    st.title("Lista de Convidados")
    # Caminho do arquivo da logo. Substitua 'path_to_logo.png' pelo caminho correto do arquivo.
    logo_path = 'bni.jpg'
    # Exibindo a logo na página
    st.image(logo_path, use_column_width=True)

    # Campo de busca por nome
    name_filter = st.text_input("Buscar por nome:")
    filtered_data = get_data(name_filter)

    # Paginação
    items_per_page = 20
      # Defina quantos itens por página você deseja
    page_number = st.number_input(label="Selecione a página", min_value=1, max_value=max(1, len(filtered_data) // items_per_page + (1 if len(filtered_data) % items_per_page > 0 else 0)), step=1) - 1
    start_index = page_number * items_per_page
    end_index = start_index + items_per_page
    page_data = filtered_data[start_index:end_index]

    # Converter os dados para um DataFrame do Pandas
    data_df = pd.DataFrame(page_data)
    
    # Mapear os valores booleanos para 'Sim' e 'Não'
    bool_mapping = {0: 'Não', 1: 'Sim'}
    data_df['presente'] = data_df['presente'].map(bool_mapping)
    data_df['recebeu_kit'] = data_df['recebeu_kit'].map(bool_mapping)
    
    # Exibir a tabela no Streamlit
    st.table(data_df[['nome', 'empresa', 'presente', 'recebeu_kit']])  # Exibindo colunas desejadas

    # Ações para alterar o estado de 'presente' e 'recebeu kit'
    st.write("Alterar o estado dos campos:")
    name_to_update = st.text_input("Nome do usuário (exatamente como aparece na tabela):", key="name_to_update")
    field_to_update = st.selectbox("Campo para atualizar:", ['presente', 'recebeu kit'], key="field_to_update")
    new_status = st.radio("Novo estado:", ['Sim', 'Não'], key="new_status")

    if st.button("Atualizar"):
        if name_to_update:
            # Mapear de volta 'Sim' e 'Não' para valores booleanos
            new_value = 1 if new_status == 'Sim' else 0
            update_status(name_to_update, field_to_update, new_value)
            st.success(f"O campo '{field_to_update}' foi atualizado para {new_status} para o usuário {name_to_update}.")
            st.experimental_rerun()

# Executa a função para renderizar a tabela
render_table()