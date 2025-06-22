from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection
)

# Set credentials and connection info
AZURE_SEARCH_SERVICE = "https://ai-foundry-ai-service-rag.search.windows.net"
AZURE_SEARCH_ADMIN_KEY = "zBXsB4hzufySdD8UXojhK5akeIVGjrbkQ9c2sEsauIAzSeBkJcUC"
AZURE_STORAGE_CONNECTION = "DefaultEndpointsProtocol=https;AccountName=servsacomman;AccountKey=UeLe0StLbTjYEsH2AsTmb53+sciobvb2hTgUxco8p9pWY/vg0W45DK22lJ/mlDPTUB0GchdLoE6++AStL6SEVQ==;EndpointSuffix=core.windows.net"
container = SearchIndexerDataContainer(name="ragdatainput")


# Create indexer client with AzureKeyCredential
indexer_client = SearchIndexerClient(
    endpoint=AZURE_SEARCH_SERVICE,
    credential=AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY)  # ✅ wrap in AzureKeyCredential
)

# Define blob container
container = SearchIndexerDataContainer(name="ragdatainput")

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
