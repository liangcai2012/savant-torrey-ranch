import pandas as pd
from matplotlib import cm

def display_distribution(axes, data,  attribute,  span=None,  cumulative=False):
    attrs = {}
    for ele in li:
        if attribute not in ele:
            continue
        if ele[attribute] in attrs:
            attrs[ ele[attribute] ] += 1
        else:
            attrs[ ele[attribute] ] = 1
    x_distr = range(len(attrs))
    width = 0.8
    axes.bar(x_distr, attrs.values(), width)
    axes.xticks([i + width / 2.0 for i in x_distr ] , attrs.keys())


def display_association(fig, data, attr_x, attr_y, span_x=None, span_y=None):
    # this is to display association of two attributes. The meaning of each input should be similar to above.
    ax = fig.gca()
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

    heatmap = ax.pcolor(mat, cmap=cm.Blues, alpha=0.8)
    ax.set_xticks([i + 0.5 for i in range(len(mat.columns))])
    ax.set_xticklabels(mat.columns)
    ax.set_yticks([i + 0.5 for i in range(len(mat.index))])
    ax.set_yticklabels(mat.index)
    ax.set_xlabel(attr_x)
    ax.set_ylabel(attr_y)
    return mat
