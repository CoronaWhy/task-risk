import os

base_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_path, 'data/coronawhy/v6_text')
customized_stop_words = [
    'doi', 'preprint', 'copyright', 'peer', 'reviewed', 'org', 'https', 'et', 'al', 'author', 'figure', 
    'rights', 'reserved', 'permission', 'used', 'using', 'biorxiv', 'fig', 'fig.', 'al.', 'q', 'license',
    'di', 'la', 'il', 'del', 'le', 'della', 'dei', 'delle', 'una', 'da',  'dell',  'non', 'si', 'holder',
    'p', 'h'
]

punctuation = '!"#$%&\'()_-*+,.:;<=>?@[\\]^`{|}~'
for p in punctuation:
    customized_stop_words.append(p)
