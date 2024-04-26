# CONFIGURATION

Dobo uses a `config.toml` file for configuration, here's an example:

```toml
# config.toml
[llm]
type = "QianfanChatEndpoint"

[llm.config]
model = "ERNIE-Bot-turbo"

[embeddings]
type = "HuggingFaceBgeEmbeddings"

[embeddings.config]
model_name = "BAAI/bge-small-en"

[embeddings.config.model_kwargs]
device = "cpu"

[embeddings.config.encode_kwargs]
normalize_embeddings = true

[vectorstore]
score_threshold = 0.7

[chain]
# debug = true
# verbose = true
```

And could use environment variables or a `.env` file to store secret keys:

```sh
# .env
VAR1="some value"
VAR2="some value too"
```
