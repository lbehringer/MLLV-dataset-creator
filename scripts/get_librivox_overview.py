"""
Copyright 2024 Lyonel Behringer

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from huiAudioCorpus.dependencyInjection.DependencyInjection import DependencyInjection
import time
import os
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--database_path", type=str, default=None, help="Set directory where overview file should be created.")
    parser.add_argument("-l", "--language", type=str, default="English", help="Set the language of the books that should be retrieved.")
    parser.add_argument("--request_url", type=str, default=None, help="Set custom request URL for metadata retrieval.")
    parser.add_argument("-ts", "--start_timestamp", type=int, default=None, help="Unix timestamp which specifies the catalog date from which to start retrieval.")
    parser.add_argument("--limit_per_iteration", type=int, default=1000, help="Maximum number of results retrieved per iteration.")
    parser.add_argument("-i", "--max_iterations", type=int, default=20, help="Maximum number of iterations that should be performed.")
    args = parser.parse_args()

    if args.database_path:
        database_path = args.database_path
    else:
        repo_root_path = os.path.join(os.path.dirname(__file__), "..")
        database_dir = "database"
        database_path = os.path.join(repo_root_path, database_dir)

    os.makedirs(database_path, exist_ok=True)

    timestamp_of_retrieval = time.strftime("%Y%m%d_%H%M%S")
    step0_path = os.path.join(database_path, f"overview_{timestamp_of_retrieval}")
    config = {
        'audios_from_librivox_persistence': {
            'book_name': '',
            'save_path': '',
            'chapter_path': '',
            'limit_per_iteration': args.limit_per_iteration,
            'max_iterations': args.max_iterations,
            'start_timestamp': args.start_timestamp
        },
        'step0_overview': {
            'save_path': step0_path,
            "request_url": args.request_url,
            "language": args.language.capitalize()
        }
    }
    DependencyInjection(config).step0_overview.run()
