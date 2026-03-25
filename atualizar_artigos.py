import requests
import xml.etree.ElementTree as ET
from datetime import datetime

def buscar_artigos(orcids, limite):
    artigos = []
    para_obter = limite
    
    for orcid in orcids:
        url = f"https://api.openalex.org/works?filter=author.orcid:https://orcid.org/{orcid}&sort=publication_date:desc&per-page={para_obter}"
        resposta = requests.get(url)
        dados = resposta.json()
        
        for obra in dados.get('results', []):
            titulo = obra.get('title', 'Sem título')
            link = obra.get('doi', '')
            data_pub = obra.get('publication_date', '')
            
            artigos.append({
                'titulo': titulo,
                'link': link,
                'data': data_pub
            })
            
    artigos_ordenados = sorted(artigos, key=lambda x: x['data'], reverse=True)
    return artigos_ordenados[:limite]

def gerar_rss(artigos, arquivo_saida):
    rss = ET.Element("rss", version="2.0")
    canal = ET.SubElement(rss, "channel")
    
    titulo_canal = ET.SubElement(canal, "title")
    titulo_canal.text = "Últimos Artigos Publicados"
    
    link_canal = ET.SubElement(canal, "link")
    link_canal.text = "https://github.com"
    
    desc_canal = ET.SubElement(canal, "description")
    desc_canal.text = "Feed automatizado de artigos científicos"
    
    for art in artigos:
        item = ET.SubElement(canal, "item")
        
        titulo_item = ET.SubElement(item, "title")
        titulo_item.text = art['titulo']
        
        link_item = ET.SubElement(item, "link")
        link_item.text = art['link']
        
        data_item = ET.SubElement(item, "pubDate")
        data_item.text = art['data']

    arvore = ET.ElementTree(rss)
    ET.indent(arvore, space="\t", level=0)
    arvore.write(arquivo_saida, encoding="utf-8", xml_declaration=True)

def principal():
    lista_orcids = [
        '0000-0001-5895-9669',
        '0000-0003-3783-9283'
    ]
    limite_total = 20
    
    artigos_recentes = buscar_artigos(lista_orcids, limite_total)
    gerar_rss(artigos_recentes, 'feed.xml')

if __name__ == '__main__':
    principal()
