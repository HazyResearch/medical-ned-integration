'''
File: generate_mapping.py
Description: Maps each concept (CUI) in UMLS to a structured entity (QID) in WikiData.
'''
from tqdm import tqdm
from pathlib import Path
import pandas as pd
import sys
import logging
from importlib import reload
import json
import os
import argparse

from bootleg.end2end.extract_mentions import extract_mentions
from bootleg.utils.parser.parser_utils import parse_boot_and_emm_args
from bootleg.utils.utils import load_yaml_file
from bootleg.run import run_model
from bootleg.end2end.bootleg_annotator import BootlegAnnotator
from utils import load_concepts, load_types, load_descriptions, save_mapping

def load_UMLS_data(in_file, semantic_network_in_file, out_file):
    '''
    Description: Load UMLS data and store in Pandas DataFrame.
    Input:
        in_file (Path): path to UMLS data store. Download and unzip from 
                        https://www.nlm.nih.gov/research/umls/licensedcontent/umlsknowledgesources.html
        semantic_network_in_file (Path): path to UMLS semantic network. Download and unzip from 
                                         https://lhncbc.nlm.nih.gov/semanticnetwork/
        out_file (Path): path to store processed dataframe
    Returns:
        umls_df (pd.DataFrame): Pandas DataFrame with UMLS data
    '''
    if(os.path.exists(out_file)):
        print(f"Loading UMLS data from {out_file}")
        return pd.read_feather(out_file)

    umls_df = load_concepts(in_file)
    load_types(in_file, semantic_network_in_file, umls_df)
    load_descriptions(in_file, umls_df)
    
    print(f"Saving UMLS data to {out_file}")
    umls_df.to_feather(out_file)
        
    return umls_df

def generateMapping(umls_df):
    '''
    Description: We use Bootleg, an off-the-shelf entity linker, to map each concept (CUI) in 
    UMLS to a structured entity (QID) in WikiData. Please run "bash download_models_and_data.sh"
    prior to executing this function.
    Input: 
        umls_df (pd.DataFrame): UMLS data stored in a Pandas dataframe. 
                                Generated using load_UMLS_data()
    Returns:
    '''
    # Set logger
    reload(logging)
    logging.basicConfig(stream=sys.stdout, format="%(asctime)s %(message)s", level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Set file paths for data and model
    root_dir = Path(".")
    data_dir = root_dir / "data"
    entity_dir = data_dir / "entity_db"
    cand_map = entity_dir / "entity_mappings/alias2qids.json"
    model_dir = root_dir / "models"
    
    device = 0 #Set this to -1 if a GPU with at least 12Gb of memory is not available
    
    # Save UMLS data in jsonlines format and extract mentions from UMLS titles    
    out_file = data_dir / "umls_data_bootleg.jsonl"
    if(os.path.exists(out_file)==False): 
        umls_sents = [{'sentence': s['umls_title'], 'cui': s['umls_cui']} for i, s in umls_df.iterrows()]
        with open(data_dir / "umls_data.jsonl", 'w') as f:
            f.write('\n'.join(map(json.dumps, umls_sents)))
        extract_mentions(data_dir / "umls_data.jsonl", out_file, cand_map, verbose=True)
    
    
    # Set config arguments for entity linker
    config_in_path = model_dir / "bootleg_uncased/bootleg_config.yaml"
    config_args = load_yaml_file(config_in_path)
    config_args["run_config"]["dataset_threads"] = 8
    config_args["run_config"]["log_level"] = "info"
    config_args["emmental"]["model_path"] = str(model_dir / "bootleg_uncased/bootleg_wiki.pth")
    config_args["data_config"]["entity_dir"] = str(entity_dir)
    config_args["data_config"]["alias_cand_map"] = "alias2qids.json"
    config_args["data_config"]["data_dir"] = str(data_dir)
    config_args["data_config"]["test_dataset"]["file"] = out_file.name
    config_args["emmental"]["device"] = device
    config_args = parse_boot_and_emm_args(config_args)
    
    # Run entity linker
    bootleg_label_file = "./bootleg-logs/bootleg_wiki/umls_data_bootleg/bootleg_wiki/bootleg_labels.jsonl"
    if(os.path.exists(bootleg_label_file) == False):
        bootleg_label_file, _ = run_model(mode="dump_preds", config=config_args)
        
    # Save mapping
    out_file = Path('./mapping.feather')
    save_mapping(bootleg_label_file, umls_df, out_file)
    print(f"Saved mapping to {out_file}")
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='generate_mapping.py')
    parser.add_argument("--umls_data_dir", help="Path to UMLS data.", default="./umls_data/2017AA")
    parser.add_argument("--umls_sem_net", help="Path to UMLS semantic network.", default="./umls_sem_net/2017AA")
    args = parser.parse_args()

    df = load_UMLS_data(Path(args.umls_data_dir), Path(args.umls_sem_net), Path('./umls_data.feather'))
    generateMapping(df)
