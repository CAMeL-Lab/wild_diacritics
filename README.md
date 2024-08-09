# Wild Diacritics

## About

Wild Diacritics paper repo (WIP).

## Data

The files for the Wild2Max and WikiNewsMax datasets can all be found in the [data](./data) directory.

## Code

CAMeLtools fork with the Wild Diacritics edits outlined in the ACL'24 paper is accessible here in [ct_wilddiac](https://github.com/CAMeL-Lab/ct_wilddiac).

You can find all the helping scripts used to generate all the numbers in the paper here in the [wilddiacs_utils](./code/wilddiacs_utils) directory.

TODO: evaluation scripts (Ossama)

## License

The Wild2Max and WikiNewsMax datasets are available under the
[Creative Commons Attribution-ShareAlike License](https://creativecommons.org/licenses/by-sa/4.0/).
See [LICENSE_CC_BY_SA](./LICENSE_CC_BY_SA) for more info.

All scripts and code in this repo are available under the MIT license.
See [LICENSE_MIT](./LICENSE_MIT) for more info.

## Citing

If you find any of our work useful or publish work using the Wild2Max or
WikiNewsMax datasets, please cite [our paper](https://arxiv.org/abs/2406.05760):

```bibtex
@misc{elgamal2024arabicdiacriticswildexploiting,
      title={Arabic Diacritics in the Wild: Exploiting Opportunities for Improved Diacritization}, 
      author={Salman Elgamal and Ossama Obeid and Tameem Kabbani and Go Inoue and Nizar Habash},
      year={2024},
      eprint={2406.05760},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2406.05760}, 
}
```

If you publish work using the WikiNewsMax dataset, please additionally cite
[the paper](https://aclanthology.org/W17-1302/) describing the original
WikiNews dataset:

```bibtex
@inproceedings{darwish-etal-2017-arabic,
    title = "{A}rabic Diacritization: Stats, Rules, and Hacks",
    author = "Darwish, Kareem  and
      Mubarak, Hamdy  and
      Abdelali, Ahmed",
    editor = "Habash, Nizar  and
      Diab, Mona  and
      Darwish, Kareem  and
      El-Hajj, Wassim  and
      Al-Khalifa, Hend  and
      Bouamor, Houda  and
      Tomeh, Nadi  and
      El-Haj, Mahmoud  and
      Zaghouani, Wajdi",
    booktitle = "Proceedings of the Third {A}rabic Natural Language Processing Workshop",
    month = apr,
    year = "2017",
    address = "Valencia, Spain",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/W17-1302",
    doi = "10.18653/v1/W17-1302",
    pages = "9--17",
    abstract = "In this paper, we present a new and fast state-of-the-art Arabic diacritizer that guesses the diacritics of words and then their case endings. We employ a Viterbi decoder at word-level with back-off to stem, morphological patterns, and transliteration and sequence labeling based diacritization of named entities. For case endings, we use Support Vector Machine (SVM) based ranking coupled with morphological patterns and linguistic rules to properly guess case endings. We achieve a low word level diacritization error of 3.29{\%} and 12.77{\%} without and with case endings respectively on a new multi-genre free of copyright test set. We are making the diacritizer available for free for research purposes.",
}
```
