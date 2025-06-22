from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    AzureOpenAIVectorizer,
    AzureOpenAIVectorizerParameters,
    SearchIndex
)

# Configuration
AZURE_SEARCH_SERVICE = "https://ser-aaif-ass-learning-dev.search.windows.net"
AZURE_SEARCH_ADMIN_KEY = "ZgkyVfMQtv4lLjbzKjTU96Be5xKAgrV10YLWYbyExeAzSeBrDlqq"
AZURE_OPENAI_ACCOUNT = "https://amart-mbzcgt6a-swedencentral.openai.azure.com/"

# Create the credential using the admin key
credential = AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY)

# Create the search index client
index_client = SearchIndexClient(endpoint=AZURE_SEARCH_SERVICE, credential=credential)

# Define fields
fields = [
    SearchField(name="parent_id", type=SearchFieldDataType.String),
    SearchField(name="title", type=SearchFieldDataType.String),
    SearchField(name="locations", type=SearchFieldDataType.Collection(SearchFieldDataType.String), filterable=True),
    SearchField(name="chunk_id", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True, facetable=True, analyzer_name="keyword"),
    SearchField(name="chunk", type=SearchFieldDataType.String, sortable=False, filterable=False, facetable=False),
    SearchField(
        name="text_vector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        vector_search_dimensions=1536,  # Fixed dimension for 'text-embedding-ada-002'
        vector_search_profile_name="myHnswProfile"
    )
]

# Configure vector search
vector_search = VectorSearch(
    algorithms=[
        HnswAlgorithmConfiguration(name="myHnsw"),
    ],
    profiles=[
        VectorSearchProfile(
            name="myHnswProfile",
            algorithm_configuration_name="myHnsw",
            vectorizer_name="myOpenAI",
        )
    ],
    vectorizers=[
        AzureOpenAIVectorizer(
            vectorizer_name="myOpenAI",
            kind="azureOpenAI",
            parameters=AzureOpenAIVectorizerParameters(
                resource_url=AZURE_OPENAI_ACCOUNT,
                deployment_name="text-embedding-ada-002",
                model_name="text-embedding-ada-002"
            ),
        )
    ],
)

# Create the search index object
index_name = "py-rag-tutorial-idx"
index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search)

# Create or update the index
result = index_client.create_or_update_index(index)
print(f"{result.name} created successfully.")

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

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (
    SplitSkill,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    AzureOpenAIEmbeddingSkill,
    EntityRecognitionSkill,
    SearchIndexerIndexProjection,
    SearchIndexerIndexProjectionSelector,
    SearchIndexerIndexProjectionsParameters,
    IndexProjectionMode,
    SearchIndexerSkillset,
    CognitiveServicesAccountKey
)

# Skillset and index names
skillset_name = "py-rag-tutorial-ss"
index_name = "py-rag-tutorial-idx"

# === Config ===
AZURE_SEARCH_SERVICE = "https://ser-aaif-ass-learning-dev.search.windows.net"
AZURE_SEARCH_ADMIN_KEY = "ZgkyVfMQtv4lLjbzKjTU96Be5xKAgrV10YLWYbyExeAzSeBrDlqq"

AZURE_AI_SERVICES_KEY = "A8BGRxSeYvCmP6VeObuHnFcJwgUTIe0IJNkeyRlUwbCUZV6w3HAiJQQJ99BFACYeBjFXJ3w3AAAAACOGYjj0"
AZURE_OPENAI_ENDPOINT = "https://amart-mbzcgt6a-swedencentral.openai.azure.com/"

# === Auth ===
search_credential = AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY)
cognitive_services_account = CognitiveServicesAccountKey(key=AZURE_AI_SERVICES_KEY)

# === Skills ===
split_skill = SplitSkill(
    description="Split skill to chunk documents",
    text_split_mode="pages",
    context="/document",
    maximum_page_length=2000,
    page_overlap_length=500,
    inputs=[
        InputFieldMappingEntry(name="text", source="/document/content")
    ],
    outputs=[
        OutputFieldMappingEntry(name="textItems", target_name="pages")
    ]
)

embedding_skill = AzureOpenAIEmbeddingSkill(
    description="Skill to generate embeddings via Azure OpenAI",
    context="/document/pages/*",
    resource_url=AZURE_OPENAI_ENDPOINT,
    deployment_name="text-embedding-ada-002",
    model_name="text-embedding-ada-002",
    dimensions=1536,
    inputs=[
        InputFieldMappingEntry(name="text", source="/document/pages/*")
    ],
    outputs=[
        OutputFieldMappingEntry(name="embedding", target_name="text_vector")
    ]
)

entity_skill = EntityRecognitionSkill(
    description="Skill to recognize locations in text",
    context="/document/pages/*",
    categories=["Location"],
    default_language_code="en",
    inputs=[
        InputFieldMappingEntry(name="text", source="/document/pages/*")
    ],
    outputs=[
        OutputFieldMappingEntry(name="locations", target_name="locations")
    ]
)

# === Index Projections ===
index_projections = SearchIndexerIndexProjection(
    selectors=[
        SearchIndexerIndexProjectionSelector(
            target_index_name=index_name,
            parent_key_field_name="parent_id",
            source_context="/document/pages/*",
            mappings=[
                InputFieldMappingEntry(name="chunk", source="/document/pages/*"),
                InputFieldMappingEntry(name="text_vector", source="/document/pages/*/text_vector"),
                InputFieldMappingEntry(name="locations", source="/document/pages/*/locations"),
                InputFieldMappingEntry(name="title", source="/document/metadata_storage_name")
            ]
        )
    ],
    parameters=SearchIndexerIndexProjectionsParameters(
        projection_mode=IndexProjectionMode.SKIP_INDEXING_PARENT_DOCUMENTS
    )
)

# === Skillset ===
skillset = SearchIndexerSkillset(
    name=skillset_name,
    description="Skillset to chunk documents and generate embeddings",
    skills=[split_skill, embedding_skill, entity_skill],
    index_projection=index_projections,
    cognitive_services_account=cognitive_services_account
)

# === Create Skillset ===
client = SearchIndexerClient(endpoint=AZURE_SEARCH_SERVICE, credential=search_credential)
client.create_or_update_skillset(skillset)
print(f"{skillset.name} created")

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes.models import (
    SearchIndexer,
    FieldMapping
)

# Create an indexer  
indexer_name = "py-rag-tutorial-idxr" 
skillset_name = "py-rag-tutorial-ss"
index_name = "py-rag-tutorial-idx"
indexer_parameters = None


AZURE_SEARCH_SERVICE = "https://ser-aaif-ass-learning-dev.search.windows.net"
AZURE_SEARCH_ADMIN_KEY = "ZgkyVfMQtv4lLjbzKjTU96Be5xKAgrV10YLWYbyExeAzSeBrDlqq"
credential = AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY)

indexer = SearchIndexer(  
    name=indexer_name,  
    description="Indexer to index documents and generate embeddings",  
    skillset_name=skillset_name,  
    target_index_name=index_name,  
    data_source_name=data_source.name,
    # Map the metadata_storage_name field to the title field in the index to display the PDF title in the search results  
    field_mappings=[FieldMapping(source_field_name="metadata_storage_name", target_field_name="title")],
    parameters=indexer_parameters
)  

# Create and run the indexer  
indexer_client = SearchIndexerClient(endpoint=AZURE_SEARCH_SERVICE, credential=credential)  
indexer_result = indexer_client.create_or_update_indexer(indexer)  

print(f' {indexer_name} is created and running. Give the indexer a few minutes before running a query.')