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

from huiAudioCorpus.transformer.TranscriptsSelectionTransformer import TranscriptsSelectionTransformer
import pandas as pd
from huiAudioCorpus.model.Audio import Audio
from huiAudioCorpus.utils.DoneMarker import DoneMarker
from huiAudioCorpus.persistence.AudioPersistence import AudioPersistence
from huiAudioCorpus.persistence.TranscriptsPersistence import TranscriptsPersistence
from tqdm import tqdm

class Step6_FinalizeDataset:

    def __init__(self, save_path: str, chapter_path: str, audio_persistence: AudioPersistence, transcripts_persistence: TranscriptsPersistence, transcripts_selection_transformer: TranscriptsSelectionTransformer):
        self.save_path = save_path
        self.audio_persistence = audio_persistence
        self.transcripts_persistence = transcripts_persistence
        self.chapter_path = chapter_path
        self.transcripts_selection_transformer = transcripts_selection_transformer
    
    def run(self):
        done_marker = DoneMarker(self.save_path)
        result = done_marker.run(self.script, delete_folder=False)
        return result

    def script(self):
        transcripts_iterator = list(self.transcripts_persistence.load_all())
        transcripts = transcripts_iterator[0]
        transcripts_ids = [sentence.id for sentence in transcripts.sentences()]
        chapters = pd.read_csv(self.chapter_path)

        transcripts_selected_ids = {}

        ids = self.audio_persistence.get_ids()
        audios = self.audio_persistence.load_all()
        for audio in tqdm(audios, total=len(ids)):
            book, chapter, index = audio.id.rsplit('_', 2)
            reader = str(chapters.loc[int(chapter) - 1]['Reader']).replace(' ', '_')  # type:ignore
            if audio.id in transcripts_ids:
                path = reader + '/' + book
                if path in transcripts_selected_ids:
                    transcripts_selected_ids[path].append(audio.id)
                else:
                    transcripts_selected_ids[path] = [audio.id]
                audio.id = path + '/wavs/' + audio.id
                self.audio_persistence.save(audio)

        for path, ids in transcripts_selected_ids.items():
            local_transcripts = self.transcripts_selection_transformer.transform(transcripts, ids)
            local_transcripts.id = path + '/metadata'
            self.transcripts_persistence.save(local_transcripts)