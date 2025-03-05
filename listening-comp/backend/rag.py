import chromadb
# setup Chroma in-memory, for easy prototyping. Can add persistence easily!
client = chromadb.Client()

# Create collection. get_collection, get_or_create_collection, delete_collection also available!
collection = client.create_collection("jlptn5-listening-comprehension")

# Add docs to the collection. Can also update and delete. Row-based API coming soon!
# Read text files from local directory
import os

text_files = []
metadatas = []
ids = []

# Assuming text files are in a 'transcripts' directory
docs_path = 'transcripts'
# Make sure the directory exists
if os.path.exists(docs_path):
    for i, filename in enumerate(os.listdir(docs_path)):
        if filename.endswith('.txt'):
            file_path = os.path.join(docs_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    text_files.append(content)
                    metadatas.append({"source": filename})
                    ids.append(f"doc{i}")
                    print(f"Added {filename} to collection")
            except Exception as e:
                print(f"Error reading {filename}: {e}")
else:
    print(f"Directory {docs_path} does not exist")

# Only add documents if we found any
if text_files:
    collection.add(
        documents=text_files,
        metadatas=metadatas, 
        ids=ids
    )
    print(f"Added {len(text_files)} documents to collection")
else:
    # Fallback to example documents if no files were found
    collection.add(
        documents=["this is textfile1","This is textfile2"],
        metadatas=[{"source":"textfile1"},{"source":"textfile2"}],
        ids=["doc1","doc2"]
    )
    print("Added example documents to collection")

# Query/search 2 most similar results. You can also .get by id
results = collection.query(
    query_texts=["This is a query document"],
    n_results=2,
    # where={"metadata_field": "is_equal_to_this"}, # optional filter
    # where_document={"$contains":"search_string"}  # optional filter
)
print(results)