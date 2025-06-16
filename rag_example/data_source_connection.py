from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection
)

# Set credentials and connection info
AZURE_SEARCH_SERVICE = "https://learning-aiss-dev.search.windows.net"
AZURE_SEARCH_ADMIN_KEY = "41AT9QAjTkSpnIw5joNpirlhs7uLyukNV6JS6rdRVVAzSeC7w1b3"
AZURE_STORAGE_CONNECTION = "DefaultEndpointsProtocol=https;AccountName=learningsadev;AccountKey=p0L0JQofnm6r+hgzkA1kVa+Y3N46hbSaTNyh4ncxDHmA97AFCQ3si/Z9UmlKiNEk13nkE75mOA9U+AStv7+hxw==;EndpointSuffix=core.windows.net"

# Create indexer client with AzureKeyCredential
indexer_client = SearchIndexerClient(
    endpoint=AZURE_SEARCH_SERVICE,
    credential=AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY)  # ✅ wrap in AzureKeyCredential
)

# Define blob container
container = SearchIndexerDataContainer(name="nasa-ebooks-pdfs-all")

# Define data source connection
data_source_connection = SearchIndexerDataSourceConnection(
    name="py-rag-tutorial-ds",
    type="azureblob",
    connection_string=AZURE_STORAGE_CONNECTION,
    container=container
)

# Create or update the data source
data_source = indexer_client.create_or_update_data_source_connection(data_source_connection)

print(f"Data source '{data_source.name}' created or updated.")
