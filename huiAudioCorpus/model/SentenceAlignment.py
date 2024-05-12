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

from huiAudioCorpus.utils.ModelToStringConverter import ToString
from huiAudioCorpus.model.Sentence import Sentence

class SentenceAlignment(ToString):
    def __init__(self, source_text: Sentence, aligned_text: Sentence, start: int, end: int, distance: float, left_is_perfect: bool = False, right_is_perfect: bool = False, is_first: bool = False, is_last: bool = False, is_perfect: bool = False, is_above_threshold: bool = False):
        self.source_text = source_text # this refers to the ASR transcript
        self.aligned_text = aligned_text # this refers to the section of the original book text that was aligned with the ASR transcript
        self.start = start
        self.end = end
        self.distance = distance
        self.left_is_perfect = left_is_perfect
        self.right_is_perfect = right_is_perfect
        self.is_first = is_first
        self.is_last = is_last
        self.is_perfect = is_perfect
        self.is_above_threshold = is_above_threshold
