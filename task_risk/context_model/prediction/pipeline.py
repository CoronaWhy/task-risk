from sklearn.base import TransformerMixin
from sklearn.pipeline import Pipeline


class DenseTransformer(TransformerMixin):

    def fit(self, X, y=None, **fit_params):
        return self

    def transform(self, X, y=None, **fit_params):
        return X.todense()


def create_pipeline_with_dense_transformer(
    pipeline_components: list,
    dense_transformer_index: int
) -> Pipeline:

    dense_transformer = DenseTransformer()
    pipeline_components.insert(dense_transformer_index, dense_transformer)
    return Pipeline(pipeline_components)
