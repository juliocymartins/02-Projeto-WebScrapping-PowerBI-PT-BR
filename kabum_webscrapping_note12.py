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

url = 'https://www.kabum.com.br/busca/xiaomi-note-12?page_number=1&page_size=20&facet_filters=eyJjYXRlZ29yeSI6WyJDZWx1bGFyICYgU21hcnRwaG9uZSJdLCJwcmljZSI6eyJtaW4iOjEwMDguNywibWF4IjoxMjAzMn19&sort=most_searched'

option = Options()
option.headless = False
driver = webdriver.Firefox(options=option)
driver.get(url)

# Lista para armazenar os produtos de todas as páginas
lista_produtos_total = []

# Loop para percorrer até o final
while True:
    slow_scroll()
    
    div_main = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[3]/div/div/div[2]/div/main')
    html_content = div_main.get_attribute('outerHTML')
    soup = BeautifulSoup(html_content, 'html.parser')
    lista_produtos = soup.find_all('div', class_='sc-cbde5b13-7 fLxdIh productCard')
    # lista_produtos mudou a class
    lista_produtos_total.extend(lista_produtos)

    # Verificar se há um botão "Próxima" e clicar nele
    next_button = driver.find_element(By.CSS_SELECTOR, '.nextLink')
    if 'true' in next_button.get_attribute('aria-disabled'):
        break  # Se o botão "Próxima" estiver desativado, sair do loop

    next_button.click() 
    time.sleep(3)  # Esperar um pouco para a próxima página carregar completamente

# Continuar com a extração dos dados a partir da lista de produtos
dados_produtos = []

for produto in lista_produtos_total:
    titulo_element = produto.find('span', class_='sc-d79c9c3f-0 nlmfp sc-cbde5b13-16 iYZziY nameCard')
    # titulo_element aterior = sc-d79c9c3f-0 nlmfp sc-cbde5b13-16 dLyTQk nameCard
    # titulo_element anterior = sc-d79c9c3f-0 nlmfp sc-6ac6cf23-16 kWpNqb nameCard
    preco_element = produto.find('span', class_='sc-6889e656-2 bYcXfg priceCard')
    # preco_element anterior = sc-6889e656-2 eDHtMY priceCard
    # preco_element anterior = sc-3b515ca1-2 chPrxA priceCard
    link_element = produto.find('a', class_='sc-cbde5b13-10 hTyWDz productLink')
    # sc-cbde5b13-10 hTyWDz productLink
    #link_element anterior = sc-6ac6cf23-10 jArChc productLink

    if titulo_element and preco_element and link_element:
        titulo = titulo_element.get_text(strip=True)
        preco = preco_element.get_text(strip=True)
        link = 'https://www.kabum.com.br' + link_element['href'] 

        # Adicionar item_id correspondente ao "Redmi Note 12"
        item_id = 1

        # Adicionar os dados a lista de produtos
        dados_produtos.append({'Título': titulo, 'Preço': preco, 'Link': link, 'item_id': item_id})

# Filtrar o DataFrame para incluir apenas produtos com "12", "12c" e "12s" no título
df = pd.DataFrame(dados_produtos)
df_filtrado = df[df['Título'].str.contains(r'\b(12|12c|12s)\b', case=False, regex=True)]

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

loja_id = 11  #loja_id

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
    link = row['Link']
    
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
