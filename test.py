import requests
from bs4 import BeautifulSoup
import networkx as nx
import matplotlib.pyplot as plt
import time
import certifi
from urllib import robotparser
import numpy as np

def can_scrape(url):
    rp = robotparser.RobotFileParser()
    rp.set_url(url + '/robots.txt') 
    #rp.read()
    try:
        # Try decoding with multiple encodings until one succeeds
        for encoding in ['utf-8', 'latin-1']:
            response = requests.get(url + '/robots.txt')
            response.raise_for_status()
            rp.parse(response.content.decode(encoding).splitlines())
            return rp.can_fetch("*", url)
    except Exception as e:
        print(f"Error reading robots.txt for {url}: {e}")
        return False  # Assume scraping is allowed if there is an issue reading the file



    #return rp.can_fetch("*", url)


def scrape_links(url, depth=1):
    if depth == 0 or not can_scrape(url):  
        return []

    try:
        #response = requests.get(url,verify=certifi.where())
        response = requests.get(url, headers={'User-Agent': 'test'})
        soup = BeautifulSoup(response.text, 'html.parser')
        links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('http')]
        return links
        
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []

def create_graph(start_url, depth):
    G = nx.Graph()
    visited = set()

    def recursive_scrape(current_url, current_depth):
        if current_depth > depth or current_url in visited or not can_scrape(current_url):
            return

        visited.add(current_url)
        links = scrape_links(current_url)

        for link in links:
            """ G.add_edge(current_url, link)
            recursive_scrape(link, current_depth + 1) """
            if G.has_edge(current_url, link):
                # Increment the edge weight
                G[current_url][link]['weight'] += 1
            else:
                # Add a new edge with weight 1
                G.add_edge(current_url, link, weight=1)
            recursive_scrape(link, current_depth + 1)

    recursive_scrape(start_url, 0)
    return G

def visualize_graph(graph):
   """  pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True, font_weight='bold', node_size=50)
    plt.show() """
   node_labels = {i: node for i, node in enumerate(graph.nodes())}
   plt.xticks(np.arange(len(node_labels)), [node_labels[i] for i in range(len(node_labels))], rotation='vertical')
   plt.yticks(np.arange(len(node_labels)), [node_labels[i] for i in range(len(node_labels))])
   adjacency_matrix = nx.to_numpy_array(graph)
   #plt.imshow(adjacency_matrix, cmap='binary', interpolation='None')
   plt.imshow(adjacency_matrix, cmap='viridis', interpolation='None')
   for i in range(adjacency_matrix.shape[0]):
        for j in range(adjacency_matrix.shape[1]):
            plt.text(j, i, int(adjacency_matrix[i, j]), ha='center', va='center', color='black')
   
   fig = plt.gcf()
   fig.set_size_inches(15,10)
   plt.title("Matrix")
   
   save_adjacency_matrix(graph,"file.txt")
   model = dtmc("file")
   print(model)
   np.savetxt("model.txt", model, fmt='%.6f', delimiter=' ', encoding='utf-8')
   
   
   #plt.show()

def save_adjacency_matrix(graph, filename):
    adjacency_matrix = nx.to_numpy_array(graph)

    # Save the adjacency matrix as a text file
    np.savetxt(filename, adjacency_matrix, fmt='%d', delimiter=',', encoding='utf-8')

    print(f"Adjacency matrix saved to {filename}")

def dtmc(file):
    # Read adjacency matrix from the text file
    adjacency_matrix = np.loadtxt(file, dtype=int)

    # Normalize rows to convert link counts to transition probabilities
    transition_matrix = adjacency_matrix.astype(float)
    row_sums = transition_matrix.sum(axis=1)
    for i in range(len(row_sums)):
        if row_sums[i] > 0:
            transition_matrix[i] /= row_sums[i]

    return transition_matrix




if __name__ == "__main__":
    start_url = "https://www.aston.ac.uk/"  # Replace with the URL you want to start from
    depth = 3  # Set the desired depth
    graph = create_graph(start_url, depth)
    visualize_graph(graph)
    
