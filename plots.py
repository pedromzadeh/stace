import numpy as np
import pandas as pd


def plot_data(df, field_names, renderer="browser"):
    """
    Scatter plot of the data in plotly.

    Parameters
    ----------
    df : pd.DataFrame
        The data to visualize.

    field_names : dict
        Specifies the fields to plot by their names. Keys are "field x",
        and values are the string defining the column title.

    Returns
    -------
    None. Opens the plots in the browser.
    """
    import plotly.io as pio
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    time = df["timestamp"]
    n_plots = len(field_names)
    n_cols = 2
    n_rows = int(np.ceil(n_plots / n_cols))

    fig = make_subplots(rows=n_rows, cols=n_cols)

    for k, col in enumerate(field_names):
        j = k % n_cols + 1
        i = k // n_cols + 1
        fig.add_trace(
            go.Scatter(
                mode="lines+markers", x=time, y=df[col], marker={"size": 10}
            ),
            row=i,
            col=j,
        )
        fig.update_yaxes(title_text=col, row=i, col=j)

    pio.renderers.default = renderer
    fig.show()
