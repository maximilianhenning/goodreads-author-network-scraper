import pandas as pd
import ast

df = pd.read_csv("./author_data.csv")

# Create edges

edges_table = []
edges_list = []
memberships_dict = {}

def edge_creator(id, influence_ids):
    edges_list = []
    if influence_ids == []:
        return edges_list
    if type(influence_ids) is str:
        influence_ids = ast.literal_eval(influence_ids)
    for influence in influence_ids:
        if influence:
            edges_list.append([int(influence), int(id)])
    return edges_list
edges_table = df.apply(lambda x: edge_creator(x.id, x.influence_ids), axis = 1)

for line in edges_table:
    for list in line:
        edges_list.append(list)

# Save edges

edges_list = [edge for edge in edges_list]
edges_df = pd.DataFrame(edges_list, columns = ["Source", "Target"])
edges_df["Type"] = "Directed"
edges_df.to_csv("./edges_incomplete.csv", index = False)

# Save nodes

nodes_df = df[["id", "name", "born_date", "died_date", "genres", "gender"]]
nodes_df.rename(columns = {"name": "Label"}, inplace = True)
print(nodes_df.head())
nodes_df.to_csv("./nodes_incomplete.csv", index = False)