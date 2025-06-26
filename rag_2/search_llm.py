# Import libraries
from azure.search.documents import SearchClient
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizableTextQuery
from azure.core.credentials import AzureKeyCredential
from azure.identity import get_bearer_token_provider
from azure.identity import DefaultAzureCredential


# Set credentials and connection info
AZURE_SEARCH_SERVICE = "https://ai-foundry-ai-service-rag.search.windows.net"
AZURE_SEARCH_ADMIN_KEY = "zBXsB4hzufySdD8UXojhK5akeIVGjrbkQ9c2sEsauIAzSeBkJcUC"
# Create the credential using the admin key
credential = AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY)
index_name = "py-rag-tutorial-idx"


openai_credential = DefaultAzureCredential()
token_provider = get_bearer_token_provider(openai_credential, "https://cognitiveservices.azure.com/.default")
AZURE_OPENAI_ACCOUNT = "https://amart-mc766w2n-eastus2.openai.azure.com/"



# openai_client = AzureOpenAI(
#      api_version="2024-06-01",
#      azure_endpoint=AZURE_OPENAI_ACCOUNT,
#      azure_ad_token_provider=token_provider
#  )

openai_client = AzureOpenAI(
    api_key="BfppO4igrIyAsncw0nnSaiyPPKtwv3JhNi4x28VcpYxg2fqeoKSXJQQJ99BFACHYHv6XJ3w3AAAAACOGx2MV",
    api_version="2024-06-01",
    azure_endpoint=AZURE_OPENAI_ACCOUNT
)

deployment_name = "gpt-4o"

search_client = SearchClient(
     endpoint=AZURE_SEARCH_SERVICE,
     index_name=index_name,
     credential=credential
 )

# Provide instructions to the model
GROUNDED_PROMPT="""
You are an AI assistant that helps users learn from the information found in the source material.
Answer the query using only the sources provided below.
Use bullets if the answer has multiple points.
If the answer is longer than 3 sentences, provide a summary.
Answer ONLY with the facts listed in the list of sources below. Cite your source when you answer the question
If there isn't enough information below, say you don't know.
Do not generate answers that don't use the sources below.
Query: {query}
Sources:\n{sources}
"""

# Provide the search query. 
# It's hybrid: a keyword search on "query", with text-to-vector conversion for "vector_query".
# The vector query finds 50 nearest neighbor matches in the search index
query="What's the NASA earth book about?"
vector_query = VectorizableTextQuery(text=query, k_nearest_neighbors=50, fields="text_vector")

# Set up the search results and the chat thread.
# Retrieve the selected fields from the search index related to the question.
# Search results are limited to the top 5 matches. Limiting top can help you stay under LLM quotas.
search_results = search_client.search(
    search_text=query,
    vector_queries= [vector_query],
    select=["title", "chunk", "locations"],
    top=5,
)

# Newlines could be in the OCR'd content or in PDFs, as is the case for the sample PDFs used for this tutorial.
# Use a unique separator to make the sources distinct. 
# We chose repeated equal signs (=) followed by a newline because it's unlikely the source documents contain this sequence.
sources_formatted = "=================\n".join([f'TITLE: {document["title"]}, CONTENT: {document["chunk"]}, LOCATIONS: {document["locations"]}' for document in search_results])

response = openai_client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": GROUNDED_PROMPT.format(query=query, sources=sources_formatted)
        }
    ],
    model=deployment_name
)

print(response.choices[0].message.content)