import pandas as pd
from matplotlib import cm

def display_distribution(axes, data,  attribute,  span=None,  cumulative=False):
    mat = pd.DataFrame(data)[attribute]
    numerical = mat.dtype.name in ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']

    if numerical and span and not cumulative:
        mat.plot(kind='hist', bins=int((mat.max() - mat.min())/ span) + 1, ax=axes )
    if numerical and span:
        mat.value_counts().sort_index().cumsum().plot(style='*-', ax=axes)
    else:
        mat.value_counts().plot(kind='bar', ax=axes)
    return mat


def display_association(axes, data, attr_x, attr_y, span_x=None, span_y=None):
    ''' this is to display association of two attributes. The meaning of each input should be similar to above.
    '''

    mat = pd.DataFrame()
    for ele in data:
        if attr_y not in ele or attr_x not in ele:
            continue
        if ele[attr_y] not in mat.index:
            xx = pd.DataFrame(0,  index=[ele[attr_y]] ,columns=mat.columns )
            mat = mat.append(xx)
        try:
            mat.loc[ele[attr_y]][ ele[attr_x]] += 1
        except KeyError:
            mat[ele[attr_x]] = pd.Series(0, index=mat.index)
            mat.loc[ele[attr_y]][ ele[attr_x]] = 1

    i = 0
    width = 0.8

    mat = (mat - mat.mean().mean()) / (mat.max().max() - mat.min().min())

    heatmap = axes.pcolor(mat, cmap=cm.Blues, alpha=0.8)
    axes.set_xticks([i + 0.5 for i in range(len(mat.columns))])
    axes.set_xticklabels(mat.columns)
    axes.set_yticks([i + 0.5 for i in range(len(mat.index))])
    axes.set_yticklabels(mat.index)
    axes.set_xlabel(attr_x)
    axes.set_ylabel(attr_y)
    return mat

# %matplotlib inline
# li = [{'key1': 'ac', 'key2': 111, 'sym': 'aaa'},
#  {'key1': 'ac', 'key2': 11, 'sym': 'bbb'}, {'key1': 'cc', 'key2': 4, 'sym': 'bbb2'},
#      {'key1': 'cc', 'key2': 4, 'sym': 'b1b'},
#      {'key1': 'cc', 'key2': 11, 'sym': 'b'},
#      {'key1': 'c', 'key2': 11, 'sym': 'b'},
#      {'key1': 'cc', 'key2': 4, 'sym': 'b'},
#      {'key1': 'cc', 'key2': 4, 'sym': '2b1b'}]
# res = display_association(fig, li,'key1', 'key2')
