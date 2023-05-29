import numpy as np
import pandas as pd


def plot_data(df, col_names=None, renderer="browser", width=800, height=1200):
    """
    Scatter plot of the input time series in plotly.

    Parameters
    ----------
    df : pd.DataFrame
        Data to visualize. Table must have column `timestamp`. All data
        found in each column will be plotted against the timestamps.

    col_names : list, optional
        Column names in df to be plotted. By default None, which plots
        all the data available in the passed data frame.

    renderer: str, optional
        Specifies where Plotly should be rendered. By default "browser".
        Other option is "notebook".

    width, height: float, optional
        Specifies dimensions of the plot.

    Returns
    -------
    None. Opens the plots in the browser.
    """
    import plotly.io as pio
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    if "timestamp" not in df.columns:
        raise ValueError("Column `timestamp` must be in the dataframe.")

    if col_names is None:
        col_names = df.columns.difference(["timestamp"])

    time = df["timestamp"]
    n_plots = len(col_names)
    n_cols = 2
    n_rows = int(np.ceil(n_plots / n_cols))

    fig = make_subplots(
            rows=n_rows,
            cols=n_cols,
            vertical_spacing=0.25,
            horizontal_spacing=0.25)

    for k, col in enumerate(col_names):
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

    fig.update_layout(width=width, height=height)
    pio.renderers.default = renderer
    fig.show()
