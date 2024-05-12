# Multilingual LibriVox (MLLV) Dataset Creator
This repository has 3 main purposes:
1. Retrieving metadata from LibriVox (`scripts/get_librivox_overview.py`)
2. ~~Analysing the audio quality of retrieved recordings (`scripts/hifi_qa.py`)~~ WIP
3. Creating datasets from selected audiobooks (`scripts/createDataset.py`)

## Installation

### Requirements

* Linux
* Anaconda 

### Setup python environment with Anaconda

Navigate to the cloned repository

Create a new conda environment
```
conda create -n dataset_creation python=3.10
conda activate dataset_creation
```

Install the package as develop python package

```
python setup.py develop
```

Installation of dependencies

(**NB: This repo currently uses the Gutenberg package (https://pypi.org/project/Gutenberg/) which requires you to install BSD-DB via your distribution's package manager.**)
```
pip install -r requirements_complete_20240317.txt
```

## Dataset Creation Workflow
1. ~~run `scripts/get_librivox_overview.py` to find speakers~~
2. ~~run `scripts/hifi_qa.py` to identify speakers with sufficient recording quality~~
3. create a dataset config in `scripts/createDatasetConfig` (some examples are given)
4. modify `scripts/createDataset.py`: adjust `external_paths`, assign the dataset config path to a variable, and assign this variable to `all_configs` (this will be streamlined at some point)
5. run `scripts/createDataset.py`; the script will likely crash in Step 3_1 (Prepare Text) and print the cases which were not normalized successfully. Currently, you need to modify the dataset config `"text_replacement"` to account for these cases.
6. If Step 5 (Align Text) fails, try manually removing the table of contents and any unread chapters from the text (in the folders for Step3 and Step3_1).
7. Once all steps have finished, you will find the metadata under `<database_folder>/final_dataset/metadata.csv` and the clean dataset under `database_folder>/final_dataset_clean` (no separate csv is created as of now).


## Known Issues
- Step 3_1 (Prepare Text): needs manual book-specific text replacements (in the corresponding dataset config .json file)
- Step 4_1 (Normalize Transcript): does not use the default text replacements but only the book-specific replacmenets
- Step 4 (Transcript Audio): Whisper predicts digits for numbers instead of spelled-out words
- Step 5 (Align Text): The current algorithm has problems with lengthy table of contents at the beginning, and alignment for selected chapters of the text is not robust

## TODO:
- [x] multilingual dataset creation (based on Whisper ASR)
- [ ] multilingual automated number normalization
- [x] dataset creation for solo readings and chapter-wise readings
- [ ] audio splits based on sentence borders

not yet released:
- [x] multiple frequency band SNR (based on VAD)
- [x] DeepXi SNR
- [x] bandwidth analysis
- [x] WVMOS integration
- [ ] room acoustics analysis
- [ ] (more detailed) F0 analysis

## Acknowledgements

This repository is largely based on the code of [HUI Audio Corpus German](https://github.com/iisys-hof/HUI-Audio-Corpus-German) - thanks for open-sourcing your code!

Further code acknowledgements:
* DeepXi (https://github.com/anicolson/DeepXi)
* WV-MOS (https://github.com/AndreevP/wvmos)
* Nemo (https://github.com/NVIDIA/NeMo-text-processing)
* Whisper (https://github.com/openai/whisper)

Inspiration from papers:
* Evelina Bakhturina, Vitaly Lavrukhin, Boris Ginsburg, Yang Zhang: Hi-Fi Multi-Speaker English TTS Dataset (https://arxiv.org/abs/2104.01497)
* Sewade Ogun, Vincent Colotte, Emmanuel Vincent: Can we use Common Voice to train a Multi-Speaker TTS system? (https://arxiv.org/abs/2210.06370)

Finally, thanks to the LibriVox community for providing an amazing public-domain resource.