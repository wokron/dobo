from langchain_community.embeddings import HuggingFaceBgeEmbeddings


embeddings = HuggingFaceBgeEmbeddings(
    model_name="BAAI/bge-small-en",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)
