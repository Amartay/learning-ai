from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection
)
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

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes.models import (
    SearchIndexer,
    FieldMapping
)


# Set credentials and connection info
AZURE_SEARCH_SERVICE = "https://ai-foundry-ai-service-rag.search.windows.net"
AZURE_SEARCH_ADMIN_KEY = "zBXsB4hzufySdD8UXojhK5akeIVGjrbkQ9c2sEsauIAzSeBkJcUC"
AZURE_STORAGE_CONNECTION = "DefaultEndpointsProtocol=https;AccountName=servsacomman;AccountKey=UeLe0StLbTjYEsH2AsTmb53+sciobvb2hTgUxco8p9pWY/vg0W45DK22lJ/mlDPTUB0GchdLoE6++AStL6SEVQ==;EndpointSuffix=core.windows.net"
container = SearchIndexerDataContainer(name="ragdatainput")


# Skillset and index names
skillset_name = "py-rag-tutorial-ss"
index_name = "py-rag-tutorial-idx"

# === Config ===

AZURE_AI_SERVICES_KEY = "3MR0WxdrilUedw3JhZhmY7HAIRUJm141YqsOmD0F83xCIv4s75ifJQQJ99BFACBsN54XJ3w3AAAAACOG5kGe"
AZURE_OPENAI_ENDPOINT = "https://amart-mc766w2n-eastus2.openai.azure.com/"

# === Auth ===
search_credential = AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY)
cognitive_services_account = CognitiveServicesAccountKey(key=AZURE_AI_SERVICES_KEY)



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




# Create an indexer  
indexer_name = "py-rag-tutorial-idxr" 
skillset_name = "py-rag-tutorial-ss"
index_name = "py-rag-tutorial-idx"
indexer_parameters = None

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