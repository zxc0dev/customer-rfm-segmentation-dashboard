import pandas as pd
import re
import shutil, zipfile, kagglehub
from pathlib import Path
import seaborn as sns
import matplotlib.pyplot as plt
import math


def df_overview(df):
    print(f"{'='*33} Shape {'='*33}")
    print(df.shape)
    print(f"{'='*33} Info {'='*33}")
    print(df.info())
    print(f"{'='*33} Columns {'='*33}")
    print(df.columns)
    print(f"{'='*33} Describe {'='*33}")
    print(df.describe())
    print(f"{'='*33} NaN {'='*33}")
    print(df.isnull().sum())
    print(f"{'='*33} Duplicates {'='*33}")
    print(df.duplicated().sum())
    print(f"{'='*33} Cardinality & Top Values {'='*33}")
    for c in df.select_dtypes(include='object').columns:
        print(c, df[c].nunique(), df[c].value_counts(normalize=True).head())


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:

    def clean_name(name: str) -> str:
        s1 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
        s2 = re.sub(r'[^a-zA-Z0-9]+', '_', s1)
        return s2.lower().strip('_')

    df.columns = [clean_name(col) for col in df.columns]
    return df


def download_data(dataset_path: str, force: bool = False):
    raw_dir = Path(__file__).resolve().parents[1] / "data" / "01_raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    has_data = any(f for f in raw_dir.iterdir() if f.is_file() and not f.name.startswith('.'))

    if not force and has_data:
        print(f"Data exists in {raw_dir}. Skipping.")
        return

    print(f"Downloading {dataset_path}...")
    downloaded_path = Path(kagglehub.dataset_download(dataset_path, force_download=force))

    if downloaded_path.suffix == ".zip":
        with zipfile.ZipFile(downloaded_path, "r") as z:
            z.extractall(raw_dir)
    elif downloaded_path.is_dir():
        for f in downloaded_path.iterdir():
            if f.is_file(): shutil.copy(f, raw_dir)
    else:
        shutil.copy(downloaded_path, raw_dir)

    print(f"Files saved to: {raw_dir}")


_VALID_KINDS = {"hist", "count", "bar", "box", "violin", "swarm"}
_DEFAULT_PALETTE = "deep"

_Y_GRID_ONLY = {"hist", "bar", "count"}


def _polish_ax(ax, xtick_rotation: int) -> None:
    """Per-axis polish that rcParams cannot handle."""

    # ── rotated tick alignment ────────────────────────────────────────────
    if xtick_rotation != 0:
        for label in ax.get_xticklabels():
            label.set_rotation(xtick_rotation)
            label.set_ha("right")           # anchors label end under tick

def plots(
    data,
    features,
    kind: str = "hist",
    value: str | None = None,
    group: str | None = None,
    hue: str | None = None,
    kde: bool = True,
    showfliers: bool = True,
    style: str = "white",
    palette: list | str | None = None,
    cols: int = 3,
    figsize_per_row: tuple = (18, 5),
    xtick_rotation: int = 45,
):
    """
    Plot multiple seaborn charts for a list of features.

    Parameters
    ----------
    data : pd.DataFrame
    features : list[str]
        One subplot per feature.
    kind : {"hist", "count", "bar", "box", "violin", "swarm"}
    value : str, optional
        y-axis column for bar plots.
    group : str, optional
        x-axis grouping column for box/violin/swarm plots.
    hue : str, optional
    kde : bool
        Overlay KDE on hist plots.
    showfliers : bool
        Show outliers in box plots.
    style : str
        Seaborn style ("white" preserves rcParams grid).
    palette : list | str | None
        Colour list or seaborn palette name; defaults to "deep".
    cols : int
        Subplot columns.
    figsize_per_row : (width, height)
    xtick_rotation : int
        X-axis tick label rotation; 45 recommended for long category names.

    Returns
    -------
    fig : Figure
    axes : np.ndarray — only used axes (length == len(features))
    """
    if kind not in _VALID_KINDS:
        raise ValueError(f"`kind` must be one of {_VALID_KINDS}, got {kind!r}")
    if not features:
        raise ValueError("`features` must not be empty.")
    if kind == "bar" and value is None:
        raise ValueError("`value` must be set when kind='bar'.")

    _pal    = palette or _DEFAULT_PALETTE
    _color0 = sns.color_palette(_pal)[0]

    sns.set_theme(style=style, rc={"axes.grid": True})
    sns.set_palette(_pal)

    n    = len(features)
    rows = math.ceil(n / cols)

    fig, axes = plt.subplots(
        rows, cols,
        figsize=(figsize_per_row[0], figsize_per_row[1] * rows),
        squeeze=False,
    )
    axes_flat = axes.ravel()

    for ax, feature in zip(axes_flat, features):

        grouped_kw = dict(
            data=data,
            x=group if group else feature,
            y=feature if group else None,
            hue=hue,
            palette=_pal if hue else None,
            color=_color0 if not hue else None,
            ax=ax,
        )

        if kind == "hist":
            sns.histplot(
                data=data, x=feature,
                hue=hue, kde=kde,
                palette=_pal if hue else None,
                color=_color0 if not hue else None,
                ax=ax,
            )

        elif kind == "count":
            sns.countplot(
                data=data, x=feature,
                hue=hue,
                palette=_pal if hue else None,
                color=_color0 if not hue else None,
                ax=ax,
            )
            for container in ax.containers:
                ax.bar_label(container, fmt="%d", padding=3)

        elif kind == "bar":
            sns.barplot(
                data=data, x=feature, y=value,
                hue=hue,
                palette=_pal if hue else None,
                color=_color0 if not hue else None,
                ax=ax,
            )
            for container in ax.containers:
                ax.bar_label(container, fmt="%.2f", padding=3)

        elif kind == "box":
            sns.boxplot(**grouped_kw, showfliers=showfliers)

        elif kind == "violin":
            sns.violinplot(**grouped_kw)

        elif kind == "swarm":
            sns.swarmplot(**grouped_kw, dodge=hue is not None)

        ax.set_title(feature)
        ax.set_xlabel("")

        # ── grid: y-only for bar-family, both axes for distribution plots ──
        if kind in _Y_GRID_ONLY:
            ax.grid(True,  axis="y")
            ax.grid(False, axis="x")

        _polish_ax(ax, xtick_rotation)

    for ax in axes_flat[n:]:
        ax.set_visible(False)

    fig.tight_layout()
    return fig, axes_flat[:n]