# Projeto de Web Scrapping
Projeto de Web Scraping - Acompanhamento de Preços de Smartphones

### LINK PARA DASHBOARD NO POWER B.I. : https://app.powerbi.com/view?r=eyJrIjoiMjU0OThlOTYtYTBjYy00MzE1LWFiMGMtOGY0MDJkODY5MDBlIiwidCI6IjE3NGZkYjA3LWY1YjYtNDc4Zi05MDdmLTY4NWY3ZDVkMGRhNCJ9

## Descrição do Projeto
Este projeto consiste em um processo de web scraping utilizando a biblioteca Selenium do Python para extrair dados de cinco e-commerces do Brasil.
O objetivo foi minerar informações sobre três smartphones muito populares e amplamente vendidos no Brasil: 

### Xiaomi Redmi Note 12
<img align="center" alt="Coding" width="400" src="https://cdn.awsli.com.br/600x700/1257/1257905/produto/229474411/note-12-6128-x9krpxdgb7.jpg">

### Samsung Galaxy A54
<img align="center" alt="Coding" width="400" src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTyDMBpDHDB7OjoPTRIwXGxyCocvNDVIN5HCg&usqp=CAU">


### iPhone 13.
<img align="center" alt="Coding" width="400" src="https://http2.mlstatic.com/D_NQ_NP_736168-MLA47781742030_102021-O.webp">

Após a extração, foram aplicados filtros utilizando bibliotecas Python (como Pandas), para obter apenas os dados específicos sobre os smartphones desejados, descartando os resultados não relevantes da pesquisa.

Os resultados foram inseridos em um banco de dados SQL, criado e modelado com antecedência no PostgreSQL.

## Dashboard no Power BI
Com base nos dados coletados, foi desenvolvido um dashboard interativo no Power BI. 
Este dashboard permite aos usuários visualizar de forma clara e concisa informações como título, preço e link dos smartphones disponíveis em diferentes lojas. 
Além disso, oferece a funcionalidade de acompanhar a variação de preço, permitindo ao usuário ordenar os resultados do menor para o maior preço.

O principal objetivo do dashboard é proporcionar uma forma eficaz de monitorar os preços dos smartphones mais populares e vendidos no país, disponíveis nos maiores e-commerces do Brasil.

## Conteúdo do Repositório
Cada arquivo ".py" do repositório foi utilizado para extrair um produto de uma determinada loja virtual.

## Contato
Para mais informações ou dúvidas, entre em contato através do e-mail [yamashitajulio@hotmail.com].

Observação importante: Pode haver alguma alteração no html dos sites utilizados no projeto, fazendo com que os códigos parem de funcionar. 

### RESPEITAR SEMPRE O SITE/SERVIDOR AO EXECUTAR ESSE TIPO DE PROGRAMA.
### ALWAYS RESPECT THE WEBSITE/SERVER WHEN RUNNING THIS TYPE OF PROGRAM.
