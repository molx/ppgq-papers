import requests
import xml.etree.ElementTree as ET
import csv

def ler_autores(caminho_arquivo):
    autores = []
    with open(caminho_arquivo, mode='r', encoding='utf-8') as arquivo:
        leitor = csv.DictReader(arquivo)
        for linha in leitor:
            autores.append(linha)
    return autores

def formatar_referencia(obra):
    autores_lista = []
    for aut in obra.get('authorships', []):
        nome = aut.get('author', {}).get('display_name', '')
        if nome:
            autores_lista.append(nome)
    
    texto_autores = "; ".join(autores_lista)
    ano = str(obra.get('publication_year', ''))
    
    revista = ""
    local_primario = obra.get('primary_location', {})
    if local_primario and local_primario.get('source'):
        revista = local_primario.get('source', {}).get('display_name', '')
    
    biblio = obra.get('biblio', {})
    volume = biblio.get('volume', '')
    fasciculo = biblio.get('issue', '')
    
    referencia = f"{texto_autores}."
    if revista:
        referencia += f" {revista},"
    if volume:
        referencia += f" v. {volume},"
    if fasciculo:
        referencia += f" n. {fasciculo},"
    if ano:
        referencia += f" {ano}."
        
    return referencia

def buscar_artigos(autores, limite):
    artigos = []
    vistos = set()
    
    for autor in autores:
        orcid_bruto = autor.get('ORCID', '').strip()
        
        if not orcid_bruto:
            continue
            
        orcid_limpo = orcid_bruto.replace('https://orcid.org/', '')
        url = f"https://api.openalex.org/works?filter=author.orcid:https://orcid.org/{orcid_limpo}&sort=publication_date:desc&per-page={limite}"
        resposta = requests.get(url)
        
        if resposta.status_code == 200:
            dados = resposta.json()
            for obra in dados.get('results', []):
                titulo = obra.get('title', 'Sem titulo')
                link = obra.get('doi', '')
                
                identificador = link if link else titulo
                
                if identificador in vistos:
                    continue
                    
                vistos.add(identificador)
                
                data_pub = obra.get('publication_date', '')
                referencia_formatada = formatar_referencia(obra)
                
                artigos.append({
                    'titulo': titulo,
                    'link': link,
                    'data': data_pub,
                    'referencia': referencia_formatada
                })
                
    artigos_ordenados = sorted(artigos, key=lambda x: str(x['data']), reverse=True)
    return artigos_ordenados[:limite]

def gerar_rss(artigos, arquivo_saida):
    rss = ET.Element("rss", version="2.0")
    canal = ET.SubElement(rss, "channel")
    
    titulo_canal = ET.SubElement(canal, "title")
    titulo_canal.text = "Artigos Publicados"
    
    link_canal = ET.SubElement(canal, "link")
    link_canal.text = "https://github.com"
    
    desc_canal = ET.SubElement(canal, "description")
    desc_canal.text = "Feed de artigos cientificos"
    
    for art in artigos:
        item = ET.SubElement(canal, "item")
        
        titulo_item = ET.SubElement(item, "title")
        titulo_item.text = art['titulo']
        
        link_item = ET.SubElement(item, "link")
        link_item.text = art['link']
        
        data_item = ET.SubElement(item, "pubDate")
        data_item.text = art['data']
        
        desc_item = ET.SubElement(item, "description")
        desc_item.text = art['referencia']

    arvore = ET.ElementTree(rss)
    ET.indent(arvore, space="    ", level=0)
    arvore.write(arquivo_saida, encoding="utf-8", xml_declaration=True)

def principal():
    autores = ler_autores('autores.csv')
    artigos_recentes = buscar_artigos(autores, 20)
    gerar_rss(artigos_recentes, 'feed.xml')

if __name__ == '__main__':
    principal()
