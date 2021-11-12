# Cross-Domain Data Integration for Named Entity Disambiguation in Biomedical Text 

Maya Varma, Laurel Orr, Sen Wu, Megan Leszczynski, Xiao Ling, Christopher Ré

<img src="splash.jpg" alt="NED splash figure.">

### Abstract

Named entity disambiguation (NED), which involves mapping textual mentions to structured entities, is particularly challenging in the medical domain due to the presence of rare entities. Existing approaches are limited by the presence of coarse-grained structural resources in biomedical knowledge bases as well as the use of training datasets that provide low coverage over uncommon resources. In this work, we address these issues by proposing a cross-domain data integration method that transfers structural knowledge from a general text knowledge base to the medical domain. We utilize our integration scheme to augment structural resources and generate a large biomedical NED dataset for pretraining. Our pretrained model with injected structural knowledge achieves state-of-the-art performance on two benchmark medical NED datasets: MedMentions and BC5CDR. Furthermore, we improve disambiguation of rare entities by up to 57 accuracy points.

Our pretraining dataset MedWiki has been released on [HuggingFace](https://huggingface.co/datasets/mvarma/medwiki).


## Usage

This codebase generates a mapping between concepts (CUIs) in UMLS and structured entities (QIDs) in WikiData. Entity linking code is adapted from [Bootleg](https://github.com/HazyResearch/bootleg). The main entry point is `generate_mapping.py`. Usage consists of the following steps:

1. Clone this repository.
```shell
$ git clone https://github.com/HazyResearch/medical-ned-integration.git
$ cd medical-ned-integration
$ pip install -r requirements.txt
```

2. Download a pretrained entity linking model (Bootleg) and associated files. 
```shell
$ bash download_models_and_data.sh
```

3. Download the UMLS Metathesaurus from https://www.nlm.nih.gov/research/umls/licensedcontent/umlsknowledgesources.html and the UMLS Semantic Network from https://lhncbc.nlm.nih.gov/semanticnetwork/. Unzip downloaded files. 
    - In our work, we used the 2017AA release of UMLS.

4. Run `generate_mapping.py`
```shell
$ python generate_mapping.py --umls_data_dir /path/to/metathesaurus --umls_sem_net /path/to/semantic_network
```

5. The mapping between UMLS concepts and QIDs in WikiData will be stored as a Pandas DataFrame in `mapping.feather`. 

## About

For questions, please reach out to `mvarma2 [at] stanford [dot] edu`. 

If you use this code in your work, please cite the following BibTeX entry:
```
@inproceedings{varma-etal-2021-cross-domain,
    title = "Cross-Domain Data Integration for Named Entity Disambiguation in Biomedical Text",
    author = "Varma, Maya  and Orr, Laurel  and Wu, Sen  and Leszczynski, Megan  and
      Ling, Xiao  and R{\'e}, Christopher",
    booktitle = "Findings of the Association for Computational Linguistics: EMNLP 2021",
    month = nov,
    year = "2021",
    address = "Punta Cana, Dominican Republic",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2021.findings-emnlp.388",
    pages = "4566--4575",
}
```