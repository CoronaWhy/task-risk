import pandas as pd
import concurrent.futures as cf
import os
import glob2
from tqdm import tqdm

def fix_doi(d):
    if d.startswith('http://'):
        return d
    elif d.startswith('doi.org'):
        return f'http://{d}'
    else:
        return f'http://doi.org/{d}'

def extract_abstract_from_json(js):
    abstract = None
    # In this particular dataset, some abstracts have multiple sections,
    # with ["abstract"][1] or later representing keywords or extra info. 
    # We only want to keep [0]["text"] in these cases. 
    if len(js["abstract"]) > 0:
        abstract = js["abstract"][0]["text"]
    # Else, ["abstract"] isn't a list and we can just grab the full text.
    else:
        abstract = js["abstract"],

    return abstract

def load_file(json_path):
    print('loading ', json_path)
    data = {}
    with open(json_path) as json_file:
        try:
            json_data = json.load(json_file)
        except:
            return None

        data['paper_id'] = json_data['paper_id']
        data['sections'] = defaultdict(str)
        data['sections']['abstract'] = extract_abstract_from_json(json_data)
        # by now only abstract and body sections, in the future, more sections can be added
        data['sections']['title'] = json_data['metadata']['title']
        data['sections']['body'] = '.\n'.join(block['text'] for block in json_data['body_text'])

    return data

def isdir(path):
    return os.path.isdir(path)

def scan_folder(folder_path, v6=False):
    documents = pd.DataFrame()
    if v6:
        for data_file in glob2.glob(os.path.join(folder_path, '*.pkl')):
            documents = pd.concat([documents, pd.read_pickle(data_file, compression="gzip")])
    else:
        for folder_path in filter(isdir, glob2.iglob(os.path.join(folder_path, "*"))):
            folder_name = os.path.basename(folder_path)
            print('Processing %s folder' % (folder_name, ))
            list_jsons = glob2.glob(os.path.join(os.path.abspath(folder_path), "**", "*.json"))
            with cf.ThreadPoolExecutor(max_workers=8) as executor:
                for raw_doc in tqdm(executor.map(load_file, list_jsons), total=len(list_jsons)):
                    if raw_doc is not None:
                        documents = pd.concat([documents, raw_doc])
    return documents

def download_dataset(data_path=None):
    import kaggle

    dataset_name = 'allen-institute-for-ai/CORD-19-research-challenge'
    if data_path is None:
        base_path = os.path.dirname(os.path.abspath(os.path.join(__file__, '..')))
        data_path = os.path.join(base_path, "raw")

    print('Downloading {}\n\tto {}'.format(dataset_name, data_path))
    # requires a kaggle auth token, go get one: https://github.com/Kaggle/kaggle-api
    kaggle.api.authenticate()
    kaggle.api.dataset_download_files(dataset_name, path=data_path, unzip=True)
