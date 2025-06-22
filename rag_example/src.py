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
# === Set up logging ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# === Configuration ===
AZURE_SEARCH_SERVICE = "https://ser-aaif-ass-learning-dev.search.windows.net"
AZURE_SEARCH_ADMIN_KEY = "ZgkyVfMQtv4lLjbzKjTU96Be5xKAgrV10YLWYbyExeAzSeBrDlqq"
AZURE_OPENAI_ACCOUNT = "https://amart-mbzcgt6a-swedencentral.openai.azure.com/"
AZURE_STORAGE_CONNECTION = "DefaultEndpointsProtocol=https;AccountName=seraaifsalearningdev;AccountKey=ccbl+2S1PRHJ6zYN3q7oiF8kG7gq24wgJZtCo4gYMmEXLJrtypBsmyNorHR4tRQ89JffdmlVJuOP+AStimSCxQ==;EndpointSuffix=core.windows.net"
AZURE_AI_SERVICES_KEY = "A8BGRxSeYvCmP6VeObuHnFcJwgUTIe0IJNkeyRlUwbCUZV6w3HAiJQQJ99BFACYeBjFXJ3w3AAAAACOGYjj0"

index_name = "py-rag-tutorial-idx"
skillset_name = "py-rag-tutorial-ss"
data_source_name = "py-rag-tutorial-ds"
indexer_name = "py-rag-tutorial-idxr"

# === Create Clients ===
credential = AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY)
index_client = SearchIndexClient(endpoint=AZURE_SEARCH_SERVICE, credential=credential)
indexer_client = SearchIndexerClient(endpoint=AZURE_SEARCH_SERVICE, credential=credential)
cognitive_services_account = CognitiveServicesAccountKey(key=AZURE_AI_SERVICES_KEY)

# === 1. Create Vector Index ===
logging.info("Creating vector index...")

fields = [
    SearchField(name="parent_id", type=SearchFieldDataType.String),
    SearchField(name="title", type=SearchFieldDataType.String),
    SearchField(name="locations", type=SearchFieldDataType.Collection(SearchFieldDataType.String), filterable=True),
    SearchField(name="chunk_id", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True, facetable=True, analyzer_name="keyword"),
    SearchField(name="chunk", type=SearchFieldDataType.String, sortable=False, filterable=False, facetable=False),
    SearchField(
        name="text_vector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        vector_search_dimensions=1536,
        vector_search_profile_name="myHnswProfile"
    )
]

vector_search = VectorSearch(
    algorithms=[HnswAlgorithmConfiguration(name="myHnsw")],
    profiles=[VectorSearchProfile(name="myHnswProfile", algorithm_configuration_name="myHnsw", vectorizer_name="myOpenAI")],
    vectorizers=[AzureOpenAIVectorizer(
        vectorizer_name="myOpenAI",
        kind="azureOpenAI",
        parameters=AzureOpenAIVectorizerParameters(
            resource_url=AZURE_OPENAI_ACCOUNT,
            deployment_name="text-embedding-ada-002",
            model_name="text-embedding-ada-002"
        )
    )]
)

index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search)
index_client.create_or_update_index(index)
logging.info(f"Index '{index_name}' created successfully.")

# === 2. Create Data Source ===
logging.info("Creating data source connection...")

container = SearchIndexerDataContainer(name="nasa-ebooks-pdfs-all")
data_source_connection = SearchIndexerDataSourceConnection(
    name=data_source_name,
    type="azureblob",
    connection_string=AZURE_STORAGE_CONNECTION,
    container=container
)
indexer_client.create_or_update_data_source_connection(data_source_connection)
logging.info(f"Data source '{data_source_name}' created or updated.")

# === 3. Create Skillset ===
logging.info("Creating skillset with Split, Embedding, and Entity skills...")

split_skill = SplitSkill(
    description="Split skill to chunk documents",
    text_split_mode="pages",
    context="/document",
    maximum_page_length=2000,
    page_overlap_length=500,
    inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
    outputs=[OutputFieldMappingEntry(name="textItems", target_name="pages")]
)

embedding_skill = AzureOpenAIEmbeddingSkill(
    description="Embedding via OpenAI",
    context="/document/pages/*",
    resource_url=AZURE_OPENAI_ACCOUNT,
    deployment_name="text-embedding-ada-002",
    model_name="text-embedding-ada-002",
    dimensions=1536,
    inputs=[InputFieldMappingEntry(name="text", source="/document/pages/*")],
    outputs=[OutputFieldMappingEntry(name="embedding", target_name="text_vector")]
)

entity_skill = EntityRecognitionSkill(
    description="Recognize locations",
    context="/document/pages/*",
    categories=["Location"],
    default_language_code="en",
    inputs=[InputFieldMappingEntry(name="text", source="/document/pages/*")],
    outputs=[OutputFieldMappingEntry(name="locations", target_name="locations")]
)

index_projections = SearchIndexerIndexProjection(
    selectors=[SearchIndexerIndexProjectionSelector(
        target_index_name=index_name,
        parent_key_field_name="parent_id",
        source_context="/document/pages/*",
        mappings=[
            InputFieldMappingEntry(name="chunk", source="/document/pages/*"),
            InputFieldMappingEntry(name="text_vector", source="/document/pages/*/text_vector"),
            InputFieldMappingEntry(name="locations", source="/document/pages/*/locations"),
            InputFieldMappingEntry(name="title", source="/document/metadata_storage_name")
        ]
    )],
    parameters=SearchIndexerIndexProjectionsParameters(
        projection_mode=IndexProjectionMode.SKIP_INDEXING_PARENT_DOCUMENTS
    )
)

skillset = SearchIndexerSkillset(
    name=skillset_name,
    description="Skillset to enrich and vectorize PDFs",
    skills=[split_skill, embedding_skill, entity_skill],
    index_projection=index_projections,
    cognitive_services_account=cognitive_services_account
)

indexer_client.create_or_update_skillset(skillset)
logging.info(f"Skillset '{skillset_name}' created or updated.")

# === 4. Create and Run Indexer ===
logging.info("Creating indexer to run the pipeline...")

indexer = SearchIndexer(
    name=indexer_name,
    description="Indexer to enrich and push data to vector index",
    skillset_name=skillset_name,
    target_index_name=index_name,
    data_source_name=data_source_name,
    field_mappings=[FieldMapping(source_field_name="metadata_storage_name", target_field_name="title")],
    parameters=None
)

indexer_client.create_or_update_indexer(indexer)
logging.info(f"Indexer '{indexer_name}' created and running. Wait a few minutes before querying.")

TARGET_URI = "https://amart-mbzcgt6a-swedencentral.openai.azure.com/openai/deployments/text-embedding-ada-002/embeddings?api-version=2023-05-15"
AZURE_OPENAI_ACCOUNT = "https://amart-mbzcgt6a-swedencentral.openai.azure.com/"
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
    #print(f"Score: {score:.4f}")
    print(f"Chunk: {chunk}\n")