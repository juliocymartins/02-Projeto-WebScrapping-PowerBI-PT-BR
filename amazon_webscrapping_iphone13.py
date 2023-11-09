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

url = 'https://www.amazon.com.br/s?k=iphone+13&i=electronics&rh=n%3A16243890011%2Cp_n_condition-type%3A13862762011%2Cp_89%3AApple&dc&__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&qid=1696300117&rnid=18120432011&ref=sr_pg_1'
option = Options()
option.headless = False
driver = webdriver.Firefox(options=option)
driver.get(url)

# Lista para armazenar os produtos de todas as páginas
lista_produtos_total = []

# Loop para percorrer até o final
while True:
    slow_scroll()
    
    div_main = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[1]/div[1]/div/span[1]/div[1]')
    html_content = div_main.get_attribute('outerHTML')
    soup = BeautifulSoup(html_content, 'html.parser')
    lista_produtos = soup.find_all('div', class_='sg-col-4-of-24 sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 sg-col s-widget-spacing-small sg-col-4-of-20')
    lista_produtos_total.extend(lista_produtos)

    # Verificar se há um botão "Próxima" e clicar nele
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, 'a.s-pagination-item.s-pagination-next.s-pagination-button.s-pagination-separator')
        next_button.click()
        time.sleep(3)  # Esperar um pouco para a próxima página carregar completamente
    except:
        break  # Se não houver botão "Próxima", sair do loop

# Continuar com a extração dos dados a partir da lista de produtos

dados_produtos = []

for produto in lista_produtos_total:
    titulo_element = produto.find('span', class_='a-size-base-plus a-color-base a-text-normal')
    preco_element = produto.find('span', class_='a-offscreen')
    link_element = produto.find('a', class_='a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal')

    if titulo_element and preco_element and link_element:
        titulo = titulo_element.get_text(strip=True)
        preco = preco_element.get_text(strip=True)
        link = 'https://www.amazon.com.br' + link_element['href'] 

        # Adicionar item_id correspondente ao "Redmi Note 12"
        item_id = 3

        dados_produtos.append({'Título': titulo, 'Preço': preco, 'Links': link, 'item_id': item_id})

df = pd.DataFrame(dados_produtos)

# Filtrar para conter 'A54' ou 'A 54' no título
# df_filtrado = df[df['Título'].str.contains(r'\b(12|12c|12s)\b', case=False, regex=True)]
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

loja_id = 8  # loja_id do banco de dados

# Excluir os produtos da loja americana antes de adicionar os novos
cur.execute(
    "DELETE FROM produtos WHERE loja_id = %s AND item_id = %s",
    (loja_id, item_id)
)

# Commit a transação
conn.commit()

# Loop para percorrer os produtos filtrados e inseri-los na tabela
for _, row in df_filtrado.iterrows():
    titulo = row['Título']
    preco_text = row['Preço']
    link = row['Links']

    # Limpar e converter o preço para um formato numérico
    preco_text = preco_text.replace('R$', '').strip()
    preco_text = preco_text.replace(',', '.')
    preco_text = preco_text.replace('.', '', preco_text.count('.') - 1)
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
