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

from huiAudioCorpus.utils.DoneMarker import DoneMarker
from huiAudioCorpus.utils.PathUtil import PathUtil
import pandas as pd
import os


class Step7_AudioRawStatistic:
    def __init__(self, save_path: str, load_path: str, path_util: PathUtil):
        self.save_path = save_path
        self.path_util = path_util
        self.load_path = load_path

    def run(self):
        done_marker = DoneMarker(self.save_path)
        result = done_marker.run(self.script, delete_folder=False)
        return result

    def script(self):
        from huiAudioCorpus.dependencyInjection.DependencyInjection import DependencyInjection
        speakers = os.listdir(self.load_path)
        all_speaker_overview_dfs = []

        # create speaker-specific overviews
        for speaker in speakers:
            if speaker == '.done':
                continue
            print('final_summary: ' + speaker)
            save_path = os.path.join(self.save_path, speaker)
            overview_save_file = os.path.join(save_path, 'overview.csv')
            self.path_util.create_folder_for_file(overview_save_file)
            local_done_marker = DoneMarker(save_path)

            if local_done_marker.is_done():
                single_speaker_overview = pd.read_csv(overview_save_file, sep='|', index_col='id')
            else:
                books = os.listdir(os.path.join(self.load_path, speaker))
                all_books_by_single_speaker_dfs = []
                for book in books:
                    load_path = os.path.join(self.load_path, speaker, book)
                    book_specific_save_file = os.path.join(save_path, f'{book}.csv')

                    # get audio info
                    di_config_audio = {
                        'audio_persistence': {
                            'load_path': load_path,
                        }
                    }
                    raw_data_audio = DependencyInjection(di_config_audio).audio_statistic_component.load_audio_files()
                    raw_data_audio['speaker'] = speaker

                    # get text info
                    di_config_text = {
                        'transcripts_persistence': {
                            'load_path': load_path,
                        }
                    }
                    raw_data_text = DependencyInjection(di_config_text).text_statistic_component.load_text_files()

                    # merge audio and text info with corresponding IDs
                    book_specific_raw_data = raw_data_audio.merge(raw_data_text, how='outer', on='id')
                    all_books_by_single_speaker_dfs.append(book_specific_raw_data)
                    # write speaker- and book-specific overview to csv file
                    book_specific_raw_data.to_csv(book_specific_save_file, sep='|')

                single_speaker_overview = pd.concat(all_books_by_single_speaker_dfs)
                local_done_marker.set_done()
            single_speaker_overview.to_csv(overview_save_file, sep='|')
            all_speaker_overview_dfs.append(single_speaker_overview)            

        # create all-speaker overview file
        all_speakers_overview = pd.concat(all_speaker_overview_dfs)
        all_speakers_overview.to_csv(os.path.join(self.save_path, 'overview.csv'), sep='|')