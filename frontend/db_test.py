import chromadb

chroma_client = chromadb.PersistentClient(path="db.sqlite3", 
    settings=chromadb.config.Settings(allow_reset=True)
)

alert_collection = chroma_client.get_collection("alert_collection")
#alert_collection = chroma_client.create_collection("alert_collection")



# alert_collection.add(
#     documents=[
#         "Alert: House is getting robbed",
#         "Alert: Your package has arrived",
#         "Alert: A black car passes by",
#     ],

#     metadatas=[
#         {'path': "filepath1.mp4"},
#         {'path': "filepath2.mp4"},
#         {'path': "filepath3.mp4"},
#     ],

#     ids=['id_1', 'id_2', 'id_3']
# )

# results = alert_collection.query(
#     query_texts=["danger"], # Chroma will embed this for you
#     n_results=1, # how many results to return
    
# )

# print(results)

def add_motion_video(alert, file_path, id):
    alert_collection.add(
        documents=[alert],
        metadatas=[{'path': file_path}],
        ids=[f"id_{id}"] # make the id unique
    )

#chroma_client.reset()

def get_all_alerts():

    results = alert_collection.get()

    return results

#print(get_all_alerts())

print(get_all_alerts())