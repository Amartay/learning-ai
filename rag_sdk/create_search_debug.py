from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex, SimpleField, SearchableField
from azure.search.documents import SearchClient
import pandas as pd

# Replace these with your values
service_endpoint = "https://learning-aiss-dev.search.windows.net"
api_key = "41AT9QAjTkSpnIw5joNpirlhs7uLyukNV6JS6rdRVVAzSeC7w1b3"
index_name = "products-index"

# Define schema
fields = [
    SimpleField(name="id", type="Edm.String", key=True, filterable=True, sortable=True),
    SearchableField(name="name", type="Edm.String", filterable=True, sortable=True),
    SimpleField(name="price", type="Edm.Double", filterable=True, sortable=True, facetable=True),
    SearchableField(name="category", type="Edm.String", filterable=True, facetable=True),
    SearchableField(name="brand", type="Edm.String", filterable=True, facetable=True),
    SearchableField(name="description", type="Edm.String")
]

# Create index
index = SearchIndex(name=index_name, fields=fields)
index_client = SearchIndexClient(endpoint=service_endpoint, credential=AzureKeyCredential(api_key))

# Delete index if it exists
try:
    index_client.delete_index(index_name)
    print(f"ℹ️ Existing index '{index_name}' deleted.")
except Exception:
    print(f"ℹ️ Index '{index_name}' did not exist.")

# Create new index
index_client.create_index(index)
print(f"✅ Index '{index_name}' created.")

# Load and prepare data
df = pd.read_csv("products.csv")
df["id"] = df["id"].astype(str)  # Ensure 'id' is string as expected

records = df.to_dict(orient="records")

# Upload documents
search_client = SearchClient(endpoint=service_endpoint, index_name=index_name, credential=AzureKeyCredential(api_key))
result = search_client.upload_documents(documents=records)
print(f"✅ Uploaded {len(result)} documents successfully.")
