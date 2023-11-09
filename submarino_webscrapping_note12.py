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

base_url = 'https://www.submarino.com.br/busca/xiaomi-redmi-note-12s-8gb-ram?limit=24&offset={}'
# filtrar 12 no titulo

option = Options()
option.headless = False
driver = webdriver.Firefox(options=option)
driver.get(base_url.format(0))  # Começando na página 0

# Lista para armazenar os produtos de todas as páginas
lista_produtos_total = []

offset = 0

# Loop para percorrer até o final
while True:
    slow_scroll()
    div_main = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/main/div/div[3]/div[2]')
    # Anteriormente era '/html/body/div[1]/div/div/main/div/div[3]/div[2]'
    html_content = div_main.get_attribute('outerHTML')
    soup = BeautifulSoup(html_content, 'html.parser')
    lista_produtos = soup.find_all('div', class_='col__StyledCol-sc-1snw5v3-0 jGlQWu src__ColGridItem-sc-cyp7mw-1 dEPgPn')
    lista_produtos_total.extend(lista_produtos)

    offset += 24  # Atualiza o offset para a próxima página
    next_url = base_url.format(offset)
    
    # Verificar se há um botão "Próxima" e atualizar a URL
    if not driver.find_elements(By.CSS_SELECTOR, '.src__Items-sc-18pu3t6-1 > li:nth-child(7) > button:nth-child(1)[disabled]'):
        # Aparentemente esse botão next muda as vezes (o css_selector pelo menos)
        driver.get(next_url)
        time.sleep(3)  # Esperar um pouco para a próxima página carregar completamente
    else:
        print("Está na última página. Não deve avançar mais.")
        break  # Sair do loop

# Restante do código permanece o mesmo

# Inicializar uma lista para armazenar os dados dos produtos
dados_produtos = []

for produto in lista_produtos_total:
    titulo_element = produto.find('h3', class_='product-name__Name-sc-1jrnqy1-0 iSRVII')
    preco_element = produto.find('span', class_='src__Text-sc-154pg0p-0 price__PromotionalPrice-sc-i1illp-1 BCJl price-info__ListPriceWithMargin-sc-z0kkvc-2 juBAtS')
    link_element = produto.find('a', class_='inStockCard__Link-sc-8xyl4s-1 ffLdXK')

    if titulo_element and preco_element and link_element:
        titulo = titulo_element.get_text(strip=True)
        preco = preco_element.get_text(strip=True)
        link = 'https://www.submarino.com.br' + link_element['href'] 
        # Adicionar item_id correspondente ao "Redmi Note 12"
        item_id = 1

        # Adicione os dados a lista de produtos
        dados_produtos.append({'Título': titulo, 'Preço': preco, 'Links': link, 'item_id': item_id})
    else:
        print("Alguns elementos não foram encontrados para este produto.")

df = pd.DataFrame(dados_produtos)

# Filtrar o DataFrame para incluir apenas produtos com "12", "12c" e "12s" no título
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

loja_id = 13  # Substitua '1' pelo loja_id que você obteve manualmente

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

