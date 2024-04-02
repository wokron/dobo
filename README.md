# Dobo

Document chat bot powered by **LLMs** and **Retrieval-Augmented Generation** (RAG).

Here's [Configuration Details](./docs/CONFIGURATION.md).

## Requirements
```console
$ pip install -r requirements.txt
```

## Deploy
```console
$ uvicorn app.main:app --reload
```

## Document
Visit `http://<host>:<port>/docs` to get the OpenAPI document.

## Scripts
Use `upload_docs.py` to upload your PDF format document:

```console
$ python ./scripts/upload_docs.py \
    --new-document-set \
    -n docset-1 \
    -d docs-dir-to-upload
```
