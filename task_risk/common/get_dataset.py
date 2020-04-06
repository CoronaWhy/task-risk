import kaggle
import os

dataset_name = 'allen-institute-for-ai/CORD-19-research-challenge'
data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw")

print('Downloading {}\n\tto {}'.format(dataset_name, data_path))
# requires a kaggle auth token, go get one: https://github.com/Kaggle/kaggle-api
kaggle.api.authenticate()
kaggle.api.dataset_download_files(dataset_name, path=data_path, unzip=True)
