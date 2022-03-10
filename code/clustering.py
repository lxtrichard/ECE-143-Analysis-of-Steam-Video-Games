import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import cv2
G = nx.Graph()
visitedN = set()
visitedE = set()
genres = set()
df = pd.read_csv('steamstore/steam.csv')

##tag clustering
for t in df['steamspy_tags']:
  tags = t.split(';')
  for i in range(len(tags)):
    if not tags[i] in visitedN:
      G.add_node(tags[i],weight=1)
      visitedN.add(tags[i])
    else:
      G.nodes[tags[i]]['weight']+=1

  for i in range(len(tags)):
    for j in range(i+1, len(tags)):
      if (tags[i], tags[j]) in visitedE or (tags[j], tags[i]) in visitedE:
        G[tags[i]][tags[j]]['weight']+=1
      else:
        G.add_edge(tags[i],tags[j],weight=1)
        visitedE.add((tags[i], tags[j]))
        visitedE.add((tags[j], tags[i]))

pos = nx.random_layout(G)
nx.drawing.nx_pylab.draw_networkx_nodes(G, pos, None, 20)
nx.drawing.nx_pylab.draw_networkx_edges(G, pos, None, 0.1)

clustering = nx.clustering(G)
nx.set_node_attributes(G, clustering, "clustering")
nx.write_gml(G, "tags.gml")

# After you have generate tags.png, you can run the following code.

# Gtag = cv2.imread("tags.png")
# plt.figure(figsize=(110, 110))
# plt.imshow(Gtag)
# plt.show()