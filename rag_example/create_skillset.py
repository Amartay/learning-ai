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

AZURE_AI_SERVICES_KEY = "BfppO4igrIyAsncw0nnSaiyPPKtwv3JhNi4x28VcpYxg2fqeoKSXJQQJ99BFACHYHv6XJ3w3AAAAACOGx2MV"
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
