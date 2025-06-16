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
AZURE_SEARCH_SERVICE = "https://learning-aiss-dev.search.windows.net"
AZURE_SEARCH_ADMIN_KEY = "41AT9QAjTkSpnIw5joNpirlhs7uLyukNV6JS6rdRVVAzSeC7w1b3"
AZURE_OPENAI_ACCOUNT = "https://learning-aais-dev.openai.azure.com/"

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
