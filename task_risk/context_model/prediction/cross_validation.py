from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import KFold
import pandas as pd


def process_kfolds(
    pipe: Pipeline,
    x_train: pd.Series,
    y_train: pd.Series,
    n_splits=10,
    error_metric=roc_auc_score
) -> pd.DataFrame:
    kfold = KFold(n_splits=n_splits)
    results = [process_fold(pipe, x_train, y_train, train_i, test_i, error_metric)
               for (train_i, test_i) in kfold.split(x_train)]
    return pd.DataFrame(results).describe()


def process_fold(
    pipe: Pipeline,
    x: pd.Series,
    y: pd.Series,
    train_index: list,
    test_index: list,
    error_metric
) -> dict:
    x_train = x.loc[train_index]
    y_train = y.loc[train_index]
    x_test = x.loc[test_index]
    y_test = y.loc[test_index]

    pipe.fit(x_train, y_train)
    if error_metric == roc_auc_score:
        preds_train = pipe.predict_proba(x_train)[:, 1]
        preds_test = pipe.predict_proba(x_test)[:, 1]
    else:
        preds_train = pipe.predict(x_train)
        preds_test = pipe.predict(x_test)
    return {
        'training_error': error_metric(y_train, preds_train),
        'testing_error': error_metric(y_test, preds_test)}
