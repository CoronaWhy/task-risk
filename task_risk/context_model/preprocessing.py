import pandas as pd


def get_df_sentences_around_n_grams_in_df_paper_on_raw_sentences(
        df_paper: pd.DataFrame,
        related_n_grams: list,
        num_sentences: int = 1) -> pd.DataFrame:
    assert num_sentences >= 0
    sentences = df_paper['sentence'].str.lower()
    return get_df_sentences_around_n_grams(df_paper, sentences, related_n_grams, num_sentences)


def get_df_sentences_around_n_grams_in_df_paper_on_umls(
        df_paper: pd.DataFrame,
        related_n_grams: list,
        num_sentences: int = 1) -> pd.DataFrame:
    sentences = df_paper['UMLS'].apply(lambda x: ' '.join(x)).str.lower()
    return get_df_sentences_around_n_grams(df_paper, sentences, related_n_grams, num_sentences)


def get_df_sentences_around_n_grams(
        df_paper: pd.DataFrame,
        sentences: pd.Series,
        related_n_grams: list,
        num_sentences: int = 1) -> pd.DataFrame:
    assert num_sentences >= 0

    sentence_index = set()
    for ngram in related_n_grams:
        sentences_matching_ngram = sentences[sentences.str.contains(ngram)].index
        sentence_index.update(sentences_matching_ngram)
        for i in range(1, num_sentences + 1):
            sentences_before_matching_ngram = sentences_matching_ngram - i
            sentences_after_matching_ngram = sentences_matching_ngram + i
            sentence_index.update(sentences_before_matching_ngram)
            sentence_index.update(sentences_after_matching_ngram)
    sentence_index = list(sentence_index)
    sentence_index = df_paper.index[df_paper.index.isin(sentence_index)]
    df_sentences_around_n_grams = df_paper.loc[sentence_index]
    return df_sentences_around_n_grams


def df_sentences_full_text_to_str(df_sentences: pd.DataFrame) -> str:
    return ' '.join(df_sentences['sentence'].str.lower())


def df_sentences_full_text_to_str_without_n_grams(
    df_sentences: pd.DataFrame,
    n_grams: list
) -> str:
    return ' '.join(df_sentences['sentence'].str.lower().str.replace('|'.join(n_grams), ''))


def df_sentences_umls_ids_to_str(df_sentences: pd.DataFrame) -> str:
    return ' '.join(df_sentences['UMLS_IDS'].apply(lambda x: ' '.join(x)))


def df_sentences_umls_ids_to_str_without_n_grams(
    df_sentences: pd.DataFrame,
    n_grams: list
) -> str:
    umls_ids = []
    for _, sent in df_sentences.iterrows():
        for umls, umls_id in zip(sent['UMLS'], sent['UMLS_IDS']):
            if umls.lower() in n_grams:
                continue
            umls_ids.append(umls_id)
    return ' '.join(umls_ids)


def df_sentences_umls_ids_to_str_without_n_gram_umls_ids(
    df_sentences: pd.DataFrame,
    umls_ids_to_drop: list
) -> str:
    umls_ids = []
    for _, sent in df_sentences.iterrows():
        for umls, umls_id in zip(sent['UMLS'], sent['UMLS_IDS']):
            if umls_id in umls_ids_to_drop:
                continue
            umls_ids.append(umls_id)
    return ' '.join(umls_ids)
