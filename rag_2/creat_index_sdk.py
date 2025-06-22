from azure.identity import DefaultAzureCredential
from azure.identity import get_bearer_token_provider
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

from azure.core.credentials import AzureKeyCredential
credential = AzureKeyCredential("YOUR_ADMIN_KEY")

# Configuration
AZURE_SEARCH_SERVICE = "https://ai-foundry-ai-service-rag.search.windows.net"
AZURE_OPENAI_ACCOUNT = "https://amart-mc766w2n-eastus2.openai.azure.com/"


 # Create a search index  
index_name = "py-rag-tutorial-idx"
index_client = SearchIndexClient(endpoint=AZURE_SEARCH_SERVICE, credential=credential)  
fields = [
    SearchField(name="parent_id", type=SearchFieldDataType.String),  
    SearchField(name="title", type=SearchFieldDataType.String),
    SearchField(name="locations", type=SearchFieldDataType.Collection(SearchFieldDataType.String), filterable=True),
    SearchField(name="chunk_id", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True, facetable=True, analyzer_name="keyword"),  
    SearchField(name="chunk", type=SearchFieldDataType.String, sortable=False, filterable=False, facetable=False),  
    SearchField(name="text_vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single), vector_search_dimensions=1024, vector_search_profile_name="myHnswProfile")
    ]  

# Configure the vector search configuration  
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
        ),  
    ], 
)  

 # Create the search index
index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search)  
result = index_client.create_or_update_index(index)  
print(f"{result.name} created")