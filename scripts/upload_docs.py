import argparse
from pathlib import Path

from sqlmodel import Session, select

import sys

sys.path.append(".")

from app import crud
from app.core.db import engine
from app.models import DocumentSet, DocumentSetCreate


def main(docset_name: str, docs_dir: Path, new_docset: bool):
    with Session(engine) as session:
        db_docset = session.exec(
            select(DocumentSet).where(DocumentSet.name == docset_name)
        ).first()
        if db_docset == None:
            if not new_docset:
                print(f'document with name "{docset_name}" already exists, exit.')
                exit(-1)

            db_docset = crud.create_document_set(
                session, DocumentSetCreate(name=docset_name)
            )

        for doc_file_path in docs_dir.rglob("*.pdf"):
            doc_name = str(doc_file_path.relative_to(docs_dir)).replace("/", ".")
            doc_file = (doc_name, doc_file_path.read_bytes())
            crud.create_document(session, doc_file, db_docset.id)

            print(f'file "{doc_name}" has been saved to document set "{docset_name}"')

        print("finish!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--name",
        "-n",
        required=True,
        help="the name of the document set you want to upload to",
    )
    parser.add_argument(
        "--docs_dir",
        "-d",
        required=True,
        help="the directory of documents for the new document set",
    )
    parser.add_argument(
        "--new-document-set",
        "-c",
        action="store_true",
        help="create a new document if it doesn't exist",
    )

    args = parser.parse_args()

    main(args.name, Path(args.docs_dir), args.new_document_set)
