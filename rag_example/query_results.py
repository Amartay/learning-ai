import logging
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchField, SearchFieldDataType, VectorSearch,
    HnswAlgorithmConfiguration, VectorSearchProfile,
    AzureOpenAIVectorizer, AzureOpenAIVectorizerParameters,
    SearchIndex, SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection, SplitSkill,
    InputFieldMappingEntry, OutputFieldMappingEntry,
    AzureOpenAIEmbeddingSkill, EntityRecognitionSkill,
    SearchIndexerSkillset, CognitiveServicesAccountKey,
    SearchIndexerIndexProjection, SearchIndexerIndexProjectionSelector,
    SearchIndexerIndexProjectionsParameters, IndexProjectionMode,
    SearchIndexer, FieldMapping
)
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizableTextQuery


# === Configuration ===
AZURE_SEARCH_SERVICE = "https://ser-aaif-ass-learning-dev.search.windows.net"
AZURE_SEARCH_ADMIN_KEY = "ZgkyVfMQtv4lLjbzKjTU96Be5xKAgrV10YLWYbyExeAzSeBrDlqq"
AZURE_OPENAI_ACCOUNT = "https://amart-mbzcgt6a-swedencentral.openai.azure.com/"
AZURE_STORAGE_CONNECTION = "DefaultEndpointsProtocol=https;AccountName=seraaifsalearningdev;AccountKey=ccbl+2S1PRHJ6zYN3q7oiF8kG7gq24wgJZtCo4gYMmEXLJrtypBsmyNorHR4tRQ89JffdmlVJuOP+AStimSCxQ==;EndpointSuffix=core.windows.net"
AZURE_AI_SERVICES_KEY = "A8BGRxSeYvCmP6VeObuHnFcJwgUTIe0IJNkeyRlUwbCUZV6w3HAiJQQJ99BFACYeBjFXJ3w3AAAAACOGYjj0"
TARGET_URI = "https://amart-mbzcgt6a-swedencentral.openai.azure.com/openai/deployments/text-embedding-ada-002/embeddings?api-version=2023-05-15"
AZURE_OPENAI_ACCOUNT = "https://amart-mbzcgt6a-swedencentral.openai.azure.com/"

index_name = "py-rag-tutorial-idx"
skillset_name = "py-rag-tutorial-ss"
data_source_name = "py-rag-tutorial-ds"
indexer_name = "py-rag-tutorial-idxr"

credential = AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY)
# Use Azure OpenAI SDK to embed query
client = AzureOpenAI(
    api_key="EnLJZ6lDrAZBLKDdNmqzKxj5LiHiJ149dH62QSvE5aIStpEIpTACJQQJ99BFACfhMk5XJ3w3AAAAACOGmX6w",
    api_version="2023-05-15",  # Adjust based on your deployment
    azure_endpoint=AZURE_OPENAI_ACCOUNT
)

query = "what's NASA's website?"
response = client.embeddings.create(
    input=query,
    model="text-embedding-ada-002"
)

logging.info(f"creating vector for input strings - {query}.")
query_vector = response.data[0].embedding


search_client = SearchClient(
    endpoint=AZURE_SEARCH_SERVICE,
    credential=credential,
    index_name=index_name
)
# Now use vector instead of relying on Azure Search to embed
results = search_client.search(
    search_text=None,
    vector_queries=[
        {
            "kind": "vector",
            "vector": query_vector,
            "kNearestNeighborsCount": 5,
            "fields": "text_vector"
        }
    ],
    select=["chunk"],
    top=1
)


logging.info("Search completed. Displaying top results.")
print("\n=== Search Results ===")
for result in results:
    score = result['@search.score']
    chunk = result.get("chunk", "[No chunk returned]")
    print(f"Score: {score:.4f}")
    print(f"Chunk: {chunk}\n")