import pandas as pd
from matplotlib import cm

# %matplotlib inline
# li = [
#     {'key1': 'ac', 'key2': 111, 'sym': 'aaa'},
#     {'key1': 'ac', 'key2': 11, 'sym': 'bbb'},
#     {'key1': 'cc', 'key2': 4, 'sym': 'bbb2'},
#     {'key1': 'cc', 'key2': 4, 'sym': 'b1b'},
#     {'key1': 'cc', 'key2': 11, 'sym': 'b'},
#     {'key1': 'c', 'key2': 11, 'sym': 'b'},
#     {'key1': 'cc', 'key2': 4, 'sym': 'b'},
#     {'key1': 'cc', 'key2': 4, 'sym': '2b1b'}
# ]
# plt.close('all')
# f, axes = plt.subplots()
# dd = display_distribution(axes, data[:200], "price_rate", 0.2)
# plt.close('all')
# f, axes = plt.subplots()
# dd = display_association(fig, li,'key1', 'key2')


def display_distribution(axes, data,  attribute,  bin_width=None,
                         cumulative=False):
    '''
    this is to display distribution of an attribute.
    '''
    mat = pd.DataFrame(data)[attribute]
    numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    numerical = mat.dtype.name in numerics

    if numerical and bin_width and not cumulative:
        bin_num = int((mat.max() - mat.min())/ bin_width) + 1
        mat.plot(kind='hist', bins=bin_num, ax=axes )
    elif numerical and bin_width:
        mat.value_counts().sort_index().cumsum().plot(style='*-', ax=axes)
    else:
        mat.value_counts().plot(kind='bar', ax=axes)
    return mat


def display_association(axes, data, attr_x, attr_y, gridsize=100):
    '''
    this is to display association of two attributes. The meaning of each
    input should be similar to above.
    '''
    spaned = pd.DataFrame(data)[[attr_x, attr_y]]
    numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    numerical = spaned[attr_x].dtype.name in numerics
    numerical = numerical and spaned[attr_y].dtype.name in numerics


    if numerical:
        spaned.plot(x=attr_x, y=attr_y, kind='hexbin', ax=axes,
                    gridsize=gridsize)
        return spaned

    mat = pd.DataFrame(0, index=spaned[attr_y].unique(),
                       columns=spaned[attr_x].unique())

    matri = spaned.groupby([attr_x, attr_y]).size().reset_index()
    for ind, ele in matri.iterrows():
        mat.loc[ele[attr_y]][ ele[attr_x]] = ele[0]

    heatmap = axes.imshow(mat)
    axes.figure.colorbar(heatmap)
    axes.set_xticks(range(len(mat.columns)))
    axes.set_xticklabels(mat.columns)
    axes.set_yticks(range(len(mat.index)))
    axes.set_yticklabels(mat.index)
    axes.set_xlabel(attr_x)
    axes.set_ylabel(attr_y)

    return mat

# li = [
#     {'key1': 'ac', 'key2': 111, 'sym': 1.1},
#     {'key1': 'ac', 'key2': 111, 'sym': 1.1},
#     {'key1': 'ac', 'key2': 111, 'sym': 6},
#     {'key1': 'ac', 'key2': 111, 'sym': 1.1},
#     {'key1': 'ac', 'key2': 111, 'sym': 1.1},
#     {'key1': 'ac', 'key2': 111, 'sym': 1.1},
#     {'key1': 'ac', 'key2': 111, 'sym': 1.1},
#     {'key1': 'ac', 'key2': 111, 'sym': 1.1},
#     {'key1': 'ac', 'key2': 11, 'sym': 1.2},
#     {'key1': 'cc', 'key2': 4, 'sym': 1.11},
#     {'key1': 'cc', 'key2': 4, 'sym': 2},
#     {'key1': 'cc', 'key2': 11, 'sym': 2.1},
#     {'key1': 'c',  'key2': 11, 'sym': 1.5},
#     {'key1': 'cc', 'key2': 4, 'sym': 2.2},
#     {'key1': 'cc', 'key2': 4, 'sym': 1.8}
# ]

# import matplotlib.pyplot as plt
# plt.close('all')
# f, axes = plt.subplots()
# dd = display_association(axes, li,'key2', 'sym', 10)
# f.savefig('sdf')
