from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import psycopg2

def slow_scroll():
    body = driver.find_element(By.TAG_NAME, 'body')
    body.send_keys(Keys.END)
    time.sleep(1)

url = 'https://www.magazineluiza.com.br/busca/iphone%2B13/?filters=category---TE%2Bsubcategory---TCSP'

option = Options()
option.headless = False
driver = webdriver.Firefox(options=option)
driver.get(url)

# Lista para armazenar os produtos de todas as páginas
lista_produtos_total = []

# Loop para percorrer até o final
while True:
    slow_scroll()
    
    div_main = driver.find_element(By.XPATH, '//html/body/div[1]/div/main/section[4]/div[3]') # tem outra opcao
    html_content = div_main.get_attribute('outerHTML')
    soup = BeautifulSoup(html_content, 'html.parser')
    lista_produtos = soup.find_all('li', class_='sc-APcvf eJDyHN')
    lista_produtos_total.extend(lista_produtos)

    # Verificar se há um botão "Próxima" e clicar nele
    try:
        next_button = driver.find_element(By.XPATH, '/html/body/div[1]/div/main/section[4]/div[4]/nav/ul/li[4]/button') 
        if 'disabled' in next_button.get_attribute('outerHTML'):
            print("Está na última página. Não deve avançar mais.")
            break  # Sair do loop
        else:
            next_button.click()
            time.sleep(6)  # Esperar um pouco para a próxima página carregar completamente
        
    except:
        print("Não foi possível encontrar o botão 'Próxima' ou não há mais páginas.")
        break  # Se não houver botão "Próxima", sair do loop

# Continuar com a extração dos dados a partir da lista de produtos

# Inicializar uma lista para armazenar os dados dos produtos
dados_produtos = []

for produto in lista_produtos_total:
    titulo_element = produto.find('h2', class_='sc-eWzREE uaEbk')
    preco_element = produto.find('p', class_='sc-kpDqfm eCPtRw sc-hoLEA kXWuGr')
    link_element = produto.find('a', class_='sc-eBMEME uPWog sc-gppfCo egZavq sc-gppfCo egZavq')

    if titulo_element and preco_element and link_element:
        titulo = titulo_element.get_text(strip=True)
        preco = preco_element.get_text(strip=True)
        link = 'https://www.magazineluiza.com.br' + link_element['href'] 
        
        # Adicionar item_id correspondente ao "Redmi Note 12"
        item_id = 3


        # Adicione os dados a lista de produtos
        dados_produtos.append({'Título': titulo, 'Preço': preco, 'Links': link, 'item_id': item_id})

# Filtrar o DataFrame para incluir apenas produtos com "12", "12c" e "12s" no título
df = pd.DataFrame(dados_produtos)
df_filtrado = df[df['Título'].str.contains('13')]

# Conectar ao banco de dados
conn = psycopg2.connect(
    dbname="xxxxxx",  # Nome do banco de dados
    user="xxxxxx",  # Nome de usuário do banco de dados
    password="xxxxxx",  # Senha do banco de dados
    host="xxxxxx",  # Endereço do servidor do banco de dados
    port="xxxxxx"  # Porta do servidor do banco de dados (padrão é 5432)
)

# Criar um cursor para executar comandos SQL
cur = conn.cursor()

loja_id = 12  # Substitua '1' pelo loja_id que você obteve manualmente

# Excluir os produtos da loja Magazine Luiza antes de adicionar os novos
cur.execute(
    "DELETE FROM produtos WHERE loja_id = %s AND item_id = %s",
    (loja_id, item_id)
)

# Commit a transação
conn.commit()


# Loop para percorrer os produtos filtrados e inseri-los na tabela
# Dentro do loop para percorrer os produtos filtrados
for _, row in df_filtrado.iterrows():
    titulo = row['Título']
    preco_text = row['Preço']
    link = row['Links']
    
    # Limpar e converter o preço para um formato numérico
    preco_text = preco_text.replace('R$', '').strip()  # Remove "R$" e espaços extras

    # Substituir vírgulas por pontos (se houver)
    preco_text = preco_text.replace(',', '.')

    # Remover pontos extras (se houver)
    preco_text = preco_text.replace('.', '', preco_text.count('.') - 1)

    # Converter para float
    preco = float(preco_text)
    
    # Inserir os dados na tabela produtos
    cur.execute(
        "INSERT INTO produtos (titulo, preco, links, loja_id, item_id) VALUES (%s, %s, %s, %s, %s)",
        (titulo, preco, link, loja_id, item_id)
    )

    # Commit a transação
    conn.commit()
# Fechar o cursor e a conexão
cur.close()
conn.close()
driver.quit()