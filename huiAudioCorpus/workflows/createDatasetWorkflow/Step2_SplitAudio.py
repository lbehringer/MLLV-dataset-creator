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

from typing import List
from huiAudioCorpus.persistence.AudioPersistence import AudioPersistence
from huiAudioCorpus.transformer.AudioSplitTransformer import AudioSplitTransformer
from huiAudioCorpus.transformer.AudioLoudnessTransformer import AudioLoudnessTransformer
from huiAudioCorpus.model.Audio import Audio
from huiAudioCorpus.utils.DoneMarker import DoneMarker
from joblib import Parallel, delayed

class Step2_SplitAudio:

    def __init__(self, 
                 audio_split_transformer: AudioSplitTransformer, 
                 audio_persistence: AudioPersistence, 
                 save_path: str, 
                 book_name: str, 
                 solo_reading: bool, 
                 sections: list, 
                 audio_loudness_transformer: AudioLoudnessTransformer, 
                 remap_sort: List[int] = None):
        self.audio_persistence = audio_persistence
        self.save_path = save_path
        self.audio_split_transformer = audio_split_transformer
        self.book_name = book_name
        self.solo_reading = solo_reading
        self.sections = sections
        self.audio_loudness_transformer = audio_loudness_transformer
        self.remap_sort = remap_sort

    def run(self):
        return DoneMarker(self.save_path).run(self.script)
    
    def script(self):
        audios = self.audio_persistence.load_all()
        if self.remap_sort:
            audios = list(audios)
            audios = [audios[i] for i in self.remap_sort]
        sections = [i+1 for i in range(len(self.audio_persistence.get_ids()))] if self.solo_reading else self.sections
        Parallel(n_jobs=1, verbose=10, batch_size="auto")(delayed(self.split_one_audio)(audio, section) for audio, section in zip(audios, sections))

    def split_one_audio(self, audio: Audio, chapter: int):
        splitted_audios = self.audio_split_transformer.transform(audio, self.book_name, chapter)
        for split_audio in splitted_audios:
            loudness_audio = self.audio_loudness_transformer.transform(split_audio)
            self.audio_persistence.save(loudness_audio)
