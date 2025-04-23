import streamlit as st
from azure.storage.blob import BlobServiceClient
import os
import pymssql
import uuid
import json
from dotenv import load_dotenv
load_dotenv()

# Configurações do Azure Storage
BlobConnectionString = os.getenv('BLOB_CONNECTION_STRING')
BlobContainerName = os.getenv('BLOB_CONTAINER_NAME')
BlobAccountName = os.getenv('BLOB_ACCOUNT_NAME')

# Configurações do Azure SQL Server
SQL_SERVER = os.getenv('SQL_SERVER')
SQL_DATABASE = os.getenv('SQL_DATABASE')
SQL_USERNAME = os.getenv('SQL_USERNAME')
SQL_PASSWORD = os.getenv('SQL_PASSWORD')


st.title('Cadastro de Produtos')

#Formulário de cadastro de Produtos
product_name = st.text_input('Nome do Produto')
product_price = st.number_input('Preço do Produto', min_value=0.0, format='%.2f')
product_description = st.text_area('Descrição do Produto')
product_image = st.file_uploader('Imagem do Produto', type=['jpg', 'png', 'jpeg'])

#Salve image on blob storage
def upload_blob(file):
    blob_service_client = BlobServiceClient.from_connection_string(BlobConnectionString)
    container_client = blob_service_client.get_container_client(BlobContainerName)
    blob_name = str(uuid.uuid4()) + file.name
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(file.read(), overwrite=True)
    image_url = f"https://{BlobAccountName}.blob.core.windows.net/{BlobContainerName}/{blob_name}"
    return image_url

def insert_product(product_name, product_price, product_description, product_image):
  try:
      image_url = upload_blob(product_image)
      conn = pymssql.connect(server=SQL_SERVER, user=SQL_USERNAME, password=SQL_PASSWORD, database=SQL_DATABASE)
      cursor = conn.cursor()
      insert_sql = f"INSERT INTO Produtos (nome, preco, descricao, imagem_url) VALUES ('{product_name}', {product_price}, '{product_description}', '{image_url}')"
      print(insert_sql)
      cursor.execute(insert_sql)
      conn.commit()
      cursor.close()
      conn.close()
      
      return True
  
  except Exception as e:
        st.error(f"Erro ao inserir produto: {e}")
        return False

def list_products():
    try:
        conn = pymssql.connect(server=SQL_SERVER, user=SQL_USERNAME, password=SQL_PASSWORD, database=SQL_DATABASE)
        cursor = conn.cursor(as_dict=True)  # Retorna os resultados como dicionários
        cursor.execute("SELECT * FROM Produtos")
        products = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return products
    
    except Exception as e:
        st.error(f"Erro ao listar produtos: {e}")
        return []

# Função para exibir a lista de produtos na tela   
def list_produtos_screen():
        products = list_products()
        print(products)
        if products:
        # Define o número de cards por linha
            cards_por_linha = 3
            # Cria as colunas iniciais
            cols = st.columns(cards_por_linha)
            for i, product in enumerate(products):
                col = cols[i % cards_por_linha]
                with col:
                    st.markdown(f"### {product['nome']}")
                    st.write(f"**Descrição:** {product['descricao']}")
                    st.write(f"**Preço:** R$ {product['preco']:.2f}")
                    if product["imagem_url"]:
                        html_img = f'<img src="{product["imagem_url"]}" width="200" height="200" alt="Imagem do produto">'
                        st.markdown(html_img, unsafe_allow_html=True)
                    st.markdown("---")
                # A cada 'cards_por_linha' produtos, se ainda houver produtos, cria novas colunas
                if (i + 1) % cards_por_linha == 0 and (i + 1) < len(products):
                    cols = st.columns(cards_por_linha)
        else:
            st.info("Nenhum produto encontrado.")

        st.info("Nenhum produto encontrado.")

if st.button('Salvar Produto'):
    insert_product(product_name, product_price, product_description, product_image)
    return_message = 'Produto salvo com sucesso'
    list_produtos_screen()
    st.success(return_message)

st.header('Produtos Cadastrados')

if st.button('Listar Produtos'):
    return_message = 'Produtos listados com sucesso'

