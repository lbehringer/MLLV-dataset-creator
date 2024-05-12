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
from huiAudioCorpus.components.AudioStatisticComponent import AudioStatisticComponent
from huiAudioCorpus.ui.Plot import Plot


class Step2_1_AudioStatistic:
    def __init__(self, save_path: str, audio_statistic_component: AudioStatisticComponent, plot: Plot):
        self.save_path = save_path
        self.audio_statistic_component = audio_statistic_component
        self.plot = plot

    def run(self):
        done_marker = DoneMarker(self.save_path)
        result = done_marker.run(self.script, delete_folder=False)
        return result

    def script(self):
        statistics, raw_data = self.audio_statistic_component.run()

        self.plot.histogram(statistics['duration']['histogram'], statistics['duration']['description'])
        self.plot.save('audioLength')
        self.plot.show()

        with open(self.save_path + '/statistic.txt', 'w') as text_file:
            for statistic in statistics.values():
                print(statistic['description'])
                print(statistic['statistic'])
                text_file.write(statistic['description'])
                text_file.write('\n')
                text_file.write(statistic['statistic'].__str__())
                text_file.write('\n')
