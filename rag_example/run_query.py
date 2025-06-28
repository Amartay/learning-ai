from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizableTextQuery
from azure.core.credentials import AzureKeyCredential


# Set credentials and connection info
AZURE_SEARCH_SERVICE = "https://ai-foundry-ai-service-rag.search.windows.net"
AZURE_SEARCH_ADMIN_KEY = "zBXsB4hzufySdD8UXojhK5akeIVGjrbkQ9c2sEsauIAzSeBkJcUC"
# Create the credential using the admin key
credential = AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY)
index_name = "py-rag-tutorial-idx"


# Vector Search using text-to-vector conversion of the querystring
query = "what's NASA's website?"  

search_client = SearchClient(endpoint=AZURE_SEARCH_SERVICE, credential=credential, index_name=index_name)
vector_query = VectorizableTextQuery(text=query, k_nearest_neighbors=50, fields="text_vector")
  
results = search_client.search(  
    search_text=query,  
    vector_queries= [vector_query],
    select=["chunk"],
    top=1
)  
  
for result in results:  
    print(f"Score: {result['@search.score']}")
    print(f"Chunk: {result['chunk']}")