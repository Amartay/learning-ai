from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection
)

# Set credentials and connection info
AZURE_SEARCH_SERVICE = "https://ser-aaif-ass-learning-dev.search.windows.net"
AZURE_SEARCH_ADMIN_KEY = "ZgkyVfMQtv4lLjbzKjTU96Be5xKAgrV10YLWYbyExeAzSeBrDlqq"
AZURE_STORAGE_CONNECTION = "DefaultEndpointsProtocol=https;AccountName=seraaifsalearningdev;AccountKey=ccbl+2S1PRHJ6zYN3q7oiF8kG7gq24wgJZtCo4gYMmEXLJrtypBsmyNorHR4tRQ89JffdmlVJuOP+AStimSCxQ==;EndpointSuffix=core.windows.net"

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
