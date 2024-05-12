"""
Copyright 2024 Lyonel Behringer

This file is based on code from https://github.com/iisys-hof/HUI-Audio-Corpus-German
and is licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from huiAudioCorpus.persistence.GutenbergBookPersistence import GutenbergBookPersistence
from huiAudioCorpus.utils.DoneMarker import DoneMarker

class Step3_DownloadText:

    def __init__(self, gutenberg_book_persistence: GutenbergBookPersistence, save_path: str):
        self.save_path = save_path
        self.gutenberg_book_persistence = gutenberg_book_persistence

    def run(self):
        return DoneMarker(self.save_path).run(self.script)
    
    def script(self):
        self.gutenberg_book_persistence.save()
