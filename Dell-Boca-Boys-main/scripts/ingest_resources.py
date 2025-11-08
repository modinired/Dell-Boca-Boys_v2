#!/usr/bin/env python3
"""Command line helper for pulling high-signal resources into memory."""
import argparse
from pathlib import Path

from app.tools.resource_ingestor import ResourceIngestor, GitHubIngestionConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ingest external knowledge")
    sub = parser.add_subparsers(dest="command", required=True)

    gh = sub.add_parser("github", help="Ingest a GitHub repository")
    gh.add_argument("repo", help="e.g. n8n-io/n8n")
    gh.add_argument("--branch", default="main")
    gh.add_argument("--token", help="GitHub personal access token")
    gh.add_argument("--max-files", type=int, default=200)

    ld = sub.add_parser("local", help="Ingest a local directory")
    ld.add_argument("path", type=Path)
    ld.add_argument("--source", default="manual")

    gd = sub.add_parser("drive", help="Ingest a Google Drive folder")
    gd.add_argument("folder_id")
    gd.add_argument("credentials", type=Path, help="Service account JSON path")
    gd.add_argument("--source", default="docs")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    ingestor = ResourceIngestor()

    if args.command == "github":
        cfg = GitHubIngestionConfig(
            repo=args.repo,
            branch=args.branch,
            token=args.token,
            max_files=args.max_files,
        )
        doc_ids = ingestor.ingest_github_repository(cfg)
    elif args.command == "local":
        doc_ids = ingestor.ingest_local_directory(args.path, source_label=args.source)
    else:
        doc_ids = ingestor.ingest_google_drive_folder(
            folder_id=args.folder_id,
            credentials_path=args.credentials,
            source_label=args.source,
        )

    print(f"Ingested {len(doc_ids)} documents into memory")


if __name__ == "__main__":
    main()
