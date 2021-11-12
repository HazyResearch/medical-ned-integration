'''
File: utils.py
Description: Helper functions for generating mappings
'''

import gzip
from tqdm import tqdm
import pandas as pd
import os
import json
from rich import print


VALID_VOCABULARIES = ['CPT', 'FMA', 'GO', 'HGNC', 'HPO', 'ICD10', \
                      'ICD10CM', 'ICD9CM', 'MDR', 'MSH', 'MTH', 'NCBI', \
                      'NCI', 'NDDF', 'NDFRT', 'OMIM', 'RXNORM', 'SNOMEDCT_US']

def load_concepts(in_file):
    '''
    Description: Load UMLS concepts and titles and store in Pandas DataFrame.
    Input:
        in_file (Path): path to UMLS data store. Downloadable from 
                        https://www.nlm.nih.gov/research/umls/licensedcontent/umlsknowledgesources.html
    Returns:
        umls_df (pd.DataFrame): Pandas DataFrame with UMLS concept identifiers and titles.
    '''
    print(f"Loading concepts from UMLS")
    cuiToTitle = {}
    for part in ['aa', 'ab']:
        with gzip.open(in_file / "META" / f"MRCONSO.RRF.{part}.gz") as f:
            for line in tqdm(f):
                fields = line.decode().strip().split('|')
                if(fields[1]!='ENG' or fields[11] not in VALID_VOCABULARIES): continue
                cui = fields[0]
                title = fields[14]
                preferredForm = (fields[2]=='P' and fields[4]=='PF') 
                if(cui not in cuiToTitle or cuiToTitle[cui][1]==0): 
                    cuiToTitle[cui] = (title, preferredForm)
    df = pd.DataFrame({'umls_cui': list(cuiToTitle.keys()), 
                       'umls_title': [cuiToTitle[c][0] for c in cuiToTitle]
                      })
    
    print(f"Loaded {df.shape[0]} concepts from UMLS\n")
    return df

def load_types(in_file, semantic_network_in_file, df):
    '''
    Description: Load UMLS types and store in Pandas DataFrame.
    Input:
        in_file (Path): path to UMLS data store. Downloadable from 
                        https://www.nlm.nih.gov/research/umls/licensedcontent/umlsknowledgesources.html
        semantic_network_in_file (Path): path to UMLS semantic network. Downloadable from 
                                         https://lhncbc.nlm.nih.gov/semanticnetwork/
        umls_df (pd.DataFrame): Pandas DataFrame with UMLS concept identifiers and titles. 
                                Will be updated to include types.
    Returns:
        None
    '''

    print(f"Loading types from UMLS")
    typeToName = {}
    with open(semantic_network_in_file / "SRDEF", 'r') as f:
        for line in tqdm(f):
            fields = line.strip().split('|')
            typeToName[fields[1]] = fields[2]
    
    cuiToType = {cui: [] for cui in df['umls_cui'].to_list()}
    all_types = set()
    with gzip.open(in_file / "META" / "MRSTY.RRF.gz") as f:
        for line in tqdm(f):
            fields = line.decode().strip().split('|')
            cui = fields[0]
            type_id = fields[1]
            if cui not in cuiToType or type_id=='UnknownType' or typeToName[type_id] in cuiToType[cui]: 
                continue
            cuiToType[cui].append(typeToName[type_id])
            all_types.add(typeToName[type_id])
    df['umls_types'] = df['umls_cui'].map(cuiToType)

    print(f"Loaded {len(all_types)} types from UMLS\n") 
    
def load_descriptions(in_file, df):
    '''
    Description: Load UMLS descriptions and store in Pandas DataFrame.
    Input:
        in_file (Path): path to UMLS data store. Downloadable from 
                        https://www.nlm.nih.gov/research/umls/licensedcontent/umlsknowledgesources.html
        umls_df (pd.DataFrame): Pandas DataFrame with UMLS concept identifiers, titles, and types. 
                                Will be updated to include descriptions.
    Returns:
        None
    '''
    print(f"Loading definitions from UMLS")
    cuiToDef = {cui: '' for cui in df['umls_cui'].to_list()}
    with gzip.open(in_file / "META" / "MRDEF.RRF.gz") as f:
        for line in f:
            fields = line.decode().strip().split('|')
            vocab = fields[4]
            cui = fields[0]
            desc = fields[5]
            if(cui not in cuiToDef): continue
            cuiToDef[cui] = desc
    df['umls_defs'] = df['umls_cui'].map(cuiToDef)
    print(f"Loaded {len(df[df['umls_defs'] != ''])} definitions from UMLS\n") 
            
def save_mapping(bootleg_label_file, umls_df, out_file):
    '''
    Description: Save mapping as Pandas DataFrame.
    Input:
        bootleg_label_file (str): path to bootleg output file
        umls_df (pd.DataFrame): Pandas DataFrame with UMLS concept identifiers, titles, and types. 
        out_file (Path): output filepath where mapping is saved
    Returns:
        None
    '''
    with open(bootleg_label_file, 'r') as f:
        lines = f.read().splitlines()
    bootleg_df = pd.json_normalize(pd.DataFrame(lines)[0].apply(json.loads))
    bootleg_df['qids'] = bootleg_df['qids'].apply(lambda x: x[0] if len(x)>0 else None)
    cuiToQid = dict(zip(bootleg_df.cui, bootleg_df.qids))
    umls_df['wikidata_qid'] = umls_df['umls_cui'].map(cuiToQid)
    umls_df.to_feather(out_file)
    
    
    