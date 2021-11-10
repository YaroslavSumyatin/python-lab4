import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from bs4.dammit import EncodingDetector
import requests
from tkinter import Tk, simpledialog

plt.figure(figsize=(10, 10))

Tk().withdraw()
START_URL = simpledialog.askstring("Input", "Insert the link to process!")
D = 0.5
start_string_to_concat = START_URL[:-1]
GLOBAL_LINKS = []


def parse_url(url):
    for a_link in GLOBAL_LINKS:
        if url == a_link[0]:
            return
    resp = requests.get(url)
    http_encoding = resp.encoding if 'charset' in resp.headers.get('content-type', '').lower() else None
    html_encoding = EncodingDetector.find_declared_encoding(resp.content, is_html=True)
    encoding = html_encoding or http_encoding
    soup = BeautifulSoup(resp.content, 'html.parser', from_encoding=encoding)
    all_links = []
    for lnk in soup.find_all('a', href=True):
        full_link = start_string_to_concat + lnk['href']
        if "http" not in lnk['href'] and full_link != url:
            all_links.append(full_link)
    if len(all_links) == 0:
        return
    for lnk in all_links:
        GLOBAL_LINKS.append((url, lnk))
        parse_url(lnk)


parse_url(START_URL)
G = nx.DiGraph()
print(GLOBAL_LINKS)
unique_links = list(set(GLOBAL_LINKS))
print(unique_links)
G.add_edges_from(unique_links)
pos = nx.spring_layout(G)
nx.draw_networkx_nodes(G, pos, node_size=500)
nx.draw_networkx_edges(G, pos, edgelist=G.edges, edge_color='black')
nx.draw_networkx_labels(G, pos)
plt.show()

pages = {}
for link in unique_links:
    pages[link[0]] = pages.get(link[0], 0) + 1

print(pages)

pages_list = list(pages)
ranks = np.full(len(pages_list), 1)
array = np.zeros(len(ranks))

print(pages_list)
for i in range(100):
    if i > 0:
        ranks = array
    for y in range(len(ranks)):
        inner_sum = 0
        for page in pages_list:
            if (page, pages_list[y]) in unique_links:
                inner_sum += ranks[pages_list.index(page)] / pages.get(page)
        array[y] = (1 - D) + D * inner_sum

arr = []
for i in range(len(ranks)):
    arr.append([pages_list[i], ranks[i]])

arr = sorted(arr, key=lambda x: x[1], reverse=True)
print(arr[:10])
