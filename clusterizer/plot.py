import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from . import algorithms
import functools


def axis_is_in_datetime_format(axis):
    """Used to check whether a previous plot on the `ax` was a time series.
    Note that `axis` is not the same as `ax`, but rather the x or y axis of `ax` (_axes_).
    """
    return type(axis.get_major_formatter()) == pd.plotting._converter.PandasAutoDateFormatter


def draw_location_time_scatter(circuit, ax=None, dot_size_to_charge_ratio=5e3, dot_colors="black", add_to_legend=False, set_title=True):
    """Draw a location (x) vs time (y) scatter plot.

    :param circuit: Circuit object containing PD series to plot
    :type circuit: class:`clusterizer.circuit.MergedCircuit`

    :param ax: Axes to draw on. Defaults to `plt.gca()`
    :type ax: class:`matplotlib.axes.Axes`, optional

    :param dot_size_to_charge_ratio: Conversion factor: picocoulomb/pixel. Set to `None` to draw all PDs the same size.
    :type dot_size_to_charge_ratio: float, optional

    :param dot_colors: A single color or a list of colors to use as dot colors.
    :type dot_colors: color, optional

    :param add_to_legend: Label circuit number?
    :type add_to_legend: bool, optional

    :param set_title: When True, axis title will be set to 'Circuit ~circuitnr~'.
    :type set_title: bool
    """
    if ax is None:
        ax = plt.gca()
    label = "Circuit {0}".format(circuit.circuitnr) if add_to_legend else None

    locations = circuit.pd['Location in meters (m)'][circuit.pd_occured]
    times = circuit.pd['Date/time (UTC)'][circuit.pd_occured]
    charges = circuit.pd['Charge (picocoulomb)'][circuit.pd_occured]
    if dot_size_to_charge_ratio is None:
        ax.scatter(x=locations, y=times, s=3, c=dot_colors, marker='8', edgecolors="none")
    else:
        ax.scatter(x=locations, y=times, s=charges/dot_size_to_charge_ratio, c=dot_colors, label=label, marker='8', edgecolors="none")

    ax.set_xlabel("Location (m)")
    ax.set_ylabel("Date")
    if set_title:
        ax.set_title("Circuit {0}".format(circuit.circuitnr))


def draw_location_hist(circuit, weigh_charges=False, ax=None, bins=None, color='black', add_to_legend=False, set_title=True):
    """Draw a histogram of PD locations.

    :param circuit: Circuit object containing PD series to plot
    :type circuit: class:`clusterizer.circuit.MergedCircuit`

    :param weigh_charges: When set to `True`, PD charges are accumulated. otherwise PD occurences are counted.
    :type weigh_charges: bool, optional

    :param bins: When set to `None` (the default value), uniformly spaced bins of width 4 meters are used. If `bins` is a sequence, it defines a monotonically increasing array of bin edges, including the rightmost edge, allowing for non-uniform bin widths.
    :type bins: Union[list,numpy.ndarray], optional

    :param ax: Axes to draw on. Defaults to `plt.gca()`
    :type ax: class:`matplotlib.axes.Axes`, optional

    :param color: Bar color
    :type color: color, optional

    :param add_to_legend: Label circuit number?
    :type add_to_legend: bool, optional

    :param set_title: When True, axis title will be set to 'Circuit ~circuitnr~'.
    :type set_title: bool

    :return: Array of histogram values, corresponding to accumulated bin content.
    :rtype: numpy.ndarray
    """
    if ax is None:
        ax = plt.gca()
    if bins is None:
        bins = np.arange(0, circuit.circuitlength+4.0, 4.0)
    hist_weights = None
    if weigh_charges:
        hist_weights = circuit.pd["Charge (picocoulomb)"]
    label = "Circuit {0}".format(circuit.circuitnr) if add_to_legend else None

    counts, _, _ = ax.hist(circuit.pd["Location in meters (m)"], weights=hist_weights, bins=bins, color=color, label=label)
    ax.set_xlabel("Location (m)")
    ax.set_ylabel("Number of PDs")
    if set_title:
        ax.set_title("Circuit {0}".format(circuit.circuitnr))


def draw_time_hist(circuit, partial_discharges=None, weigh_charges=False, ax=None, bins=None, sort=False, color='black', set_title=True):
    """
    Draw a histogram, binning partial discharges along the time dimension.

    :param circuit: Circuit object
    :type circuit: class:`clusterizer.circuit.MergedCircuit`

    :param partial_discharges: The partial discharges to be used to make the histogram. When set to None, circuit.pd[circuit.pd_occured] is used as a default.
    :type partial_discharges: class:`pandas.core.frame.DataFrame`, optional

    :param weigh_charges: When set to `True`, PD charges are accumulated. otherwise PD occurences are counted.
    :type weigh_charges: bool, optional

    :param ax: Axes to draw on. Defaults to `plt.gca()`
    :type ax: class:`matplotlib.axes.Axes`, optional

    :param bins: When set to `None` (the default value), uniformly spaced bins of 1 day are used. If `bins` is a sequence, it defines a monotonically increasing array of bin edges, including the rightmost edge, allowing for non-uniform bin widths.
    :type bins: Union[list,numpy.ndarray], optional

    :param sort: Indicates if the histogram should be sorted according to number of PDs in each bin
    :type sort: bool, optional

    :param color: Bar color
    :type color: color, optional

    :param set_title: When True, axis title will be set to 'Circuit ~circuitnr~'.
    :type set_title: bool
    """
    if ax is None:
        ax = plt.gca()
    if partial_discharges is None:
        partial_discharges = circuit.pd[circuit.pd_occured]
    time_column, location_column, charge_column = circuit.pd.columns
    convert_times = lambda s: datetime.datetime.strptime(str(s), "%Y-%m-%d %H:%M:%S")
    times = partial_discharges[time_column].apply(convert_times)
    if bins is None:
        start_time = times[times.index[0]]
        stop_time = times[times.index[-1]]
        bins = np.arange(start = start_time, stop = stop_time, step = datetime.timedelta(days=1))
    hist_weights = None
    if weigh_charges:
        hist_weights = partial_discharges[charge_column]

    hist, bins = np.histogram(times, bins, weights=hist_weights)
    width = 1

    if sort:
        hist = sorted(hist)
        center = np.arange(0, 100, 100/len(hist))
        ax.bar(center, hist, align='center', width=width, color=color)
        ax.set_xlabel("Percentage of bins")
    else:
        #bins_conv = np.array(list(map(convert_times, list(map(pd.Timestamp, bins)))))
        delta = (bins[:-1] - bins[1:])/2
        center = bins[1:] + delta
        ax.bar(center, hist, align='center', width=width, color=color)
        ax.set_xlabel("Time")
    ax.set_title("Circuit {0}, from {1} meter to {2} meter".format(circuit.circuitnr, round(partial_discharges[location_column][partial_discharges.index[0]], 1), round(partial_discharges[location_column][partial_discharges.index[-1]], 1)))
    ax.set_ylabel("Number of PDs")
    if set_title:
        ax.set_title("Circuit {0}".format(circuit.circuitnr))


def overlay_warnings(circuit, ax=None, opacity=.3, line_width=None, add_to_legend=True):
    """Draw colored lines for every warning in the circuit. Useful when the same axis was used to draw a location time scatter plot.
    Tip: use `clusterizer.plot.legend_without_duplicate_labels(ax)` instead of `ax.legend()`.

    :param circuit: Circuit object containing warning series to plot
    :type circuit: class:`clusterizer.circuit.MergedCircuit`

    :param ax: Axes to draw on. Defaults to `plt.gca()`
    :type ax: class:`matplotlib.axes.Axes`, optional

    :param opacity: Fill opacity (1=opaque; 0=invisible)
    :type opacity: float, optional

    :param line_width: Width of warning line. Defaults to 1% of circuit length.
    :type line_width: float, optional

    :param add_to_legend: Label warning colors?
    :type add_to_legend: bool, optional
    """
    overlay_cluster_collection(algorithms.warnings_to_clusters(circuit, cluster_width=line_width), ax=ax, opacity=opacity, add_to_legend=add_to_legend)


def overlay_cluster_collection(clusters, ax=None, color=None, opacity=.3, scale_opacity_by_found_by_count=True, add_to_legend=True, label=None):
    """Draw shaded rectangles matching the cluster dimensions. Useful when the same axis was used to draw a location time scatter plot.
    Tip: use `clusterizer.plot.legend_without_duplicate_labels(ax)` instead of `ax.legend()`.

    :param circuit: Cluster objects with time or location bounds defined.
    :type circuit: list of class:`clusterizer.cluster.Cluster`

    :param ax: Axes to draw on. Defaults to `plt.gca()`
    :type ax: class:`matplotlib.axes.Axes`, optional

    :param color: Fill color
    :type color: color, optional

    :param opacity: Fill opacity (1=opaque; 0=invisible)
    :type opacity: float, optional

    :param scale_opacity_by_found_by_count: When set to True, the draw opacity equals: `opacity * len(cluster.found_by)`.
    :type scale_opacity_by_found_by_count: True

    :param add_to_legend: Use the clusters' 'found_by' set as legend label?
    :type add_to_legend: bool, optional

    :param label: A custom legend label, overrides default labeling
    :type label: str, optional
    """
    for c in clusters:
        overlay_cluster(c, ax, color, opacity, scale_opacity_by_found_by_count=scale_opacity_by_found_by_count, add_to_legend=add_to_legend, label=label)


def overlay_cluster(cluster, ax=None, color=None, opacity=.2, scale_opacity_by_found_by_count=True, add_to_legend=True, label=None):
    """Draw a shaded rectangle matching the cluster dimensions. Useful when the same axis was used to draw a location time scatter plot.

    :param cluster: Cluster object with time or location bounds defined.
    :type cluster: class:`clusterizer.cluster.Cluster`

    :param ax: Axes to draw on. Defaults to `plt.gca()`
    :type ax: class:`matplotlib.axes.Axes`, optional

    :param color: Fill color
    :type color: color, optional

    :param opacity: Fill opacity (1=opaque; 0=invisible)
    :type opacity: float, optional

    :param scale_opacity_by_found_by_count: When set to True, the draw opacity equals: `opacity * len(cluster.found_by)`.
    :type scale_opacity_by_found_by_count: True

    :param add_to_legend: Use the cluster's 'found_by' set as legend label?
    :type add_to_legend: bool, optional

    :param label: A custom legend label, overrides default labeling
    :type label: str, optional
    """
    if cluster is None:
        return
    if ax is None:
        ax = plt.gca()

    # TODO: warn user when overlaying an empty plot
    show_date = cluster.time_range is not None and axis_is_in_datetime_format(ax.yaxis)

    clabel = None
    if add_to_legend:
        clabel = "Found by {}".format("; ".join(sorted(cluster.found_by)))
    if label is not None:
        clabel = label

    if color is None:
        color = generate_color_from_string(clabel)

    if scale_opacity_by_found_by_count:
        opacity = np.min([1.0, opacity * len(cluster.found_by)])

    loc = list(cluster.location_range)
    dates = cluster.time_range
    if show_date:
        overlay_boolean_series([True, True], loc=loc, ax=ax, y1=dates[0], y2=dates[1], color=color, opacity=opacity, label=clabel)
    else:
        overlay_boolean_series([True, True], loc=loc, ax=ax, color=color, opacity=opacity, label=clabel)


def overlay_boolean_series(values, loc=None, ax=None, y1=None, y2=None, color='yellow', opacity=.3, label=None):
    """Overlay a series of vertical colored stripes at locations in `loc` where the corresponding element of `values` is truthy.

    :param loc: Locations to draw boolean values. (If the plot contains binned data, `bins[:-1]` would be a logical choice.) Defaults to equal division of the x-axis.
    :type loc: Union[list,numpy.ndarray], optional

    :param ax: Axes to draw on. Defaults to `plt.gca()`
    :type ax: class:`matplotlib.axes.Axes`, optional

    :param y1: Lower edge of shaded area. Defaults to `ax.get_ylim()[0]`.
    :type y1: Union[float, list, numpy.ndarray], optional

    :param y2: Upper edge of shaded area. Defaults to `ax.get_ylim()[1]`.
    :type y2: Union[float, list, numpy.ndarray], optional

    :param color: Fill color
    :type color: color, optional

    :param opacity: Fill opacity (1=opaque; 0=invisible)
    :type opacity: float, optional

    :param label: Label to add to the legend
    :type label: str, optional
    """
    if ax is None:
        ax = plt.gca()
    ymin, ymax = ax.get_ylim()
    xmin, xmax = ax.get_xlim()
    y_lower = ymin if y1 is None else y1
    y_upper = ymax if y2 is None else y2

    if loc is None:
        loc = np.linspace(xmin, xmax, num=len(values))

    ax.fill_between(loc, y1=y_lower, y2=y_upper, where=values, color=color, alpha=opacity, label=label)

    # Omdat het gekleurde gebied misschien doorloopt tot de boven- en onderkanten van het plotgebied, wordt het plotgebied door matplotlib automatisch vergroot om dit te laten passen. Dit doen we ongedaan:
    ax.set_ylim(ymin, ymax)


def generate_color_from_string(s, matplotlib_color_map_name="rainbow", superprime=111, supermod=101, magicoffset=13):
    """Converts any string to a matplotlib color by applying a 'hash'.

    The default parameters have the special property that:
    - 'Found by DNV GL warning 1' is mapped to _yellow_.
    - 'Found by DNV GL warning 2' is mapped to _orange_.
    - 'Found by DNV GL warning 3' is mapped to _red_.
    - 'Found by DNV GL warning N' is mapped to _light green_.

    ---

    **Implementation:**

    String to integer:
        `i = (all bytes in s, casted as single integer)`
    specifically:
        `i = functools.reduce(lambda a, b: a*256 + b, map(ord, s))`

    Integer to rational ∈ [0,1):
        `r = ( ((i + magicoffset) * superprime) % supermod ) / supermod`

    Rational to color:
        `color = color_map(r)`

    :param s: String to convert
    :type s: str

    :param matplotlib_color_map_name: See [matplotlib docs](https://matplotlib.org/tutorials/colors/colormaps.html) for choosing a colormap.
    :type matplotlib_color_map_name: str, optional

    :param superprime: See implementation above.
    :type superprime: int, optional

    :param supermod: See implementation above.
    :type supermod: int, optional

    :param magicoffset: See implementation above.
    :type magicoffset: int, optional
    """

    # Quick fix

    poissonred = np.array([255, 126, 126, 255])/255.0
    dbblue = np.array([126, 206, 255, 255])/255.0
    pintayellow = np.array([255, 230, 69, 255])/255.0

    sl = s.lower()
    if sl.startswith("found by"):
        matches = []
        if "poisson" in sl:
            matches.append(poissonred)
        if "dbscan" in sl:
            matches.append(dbblue)
        if any(x in sl for x in ["dennis", "pinta", "paint"]):
            matches.append(pintayellow)
        return tuple(sum(matches) / len(matches))

    def str2int(s):
        if s is None or s == "":
            return 0
        return functools.reduce(lambda a, b: a*256 + b, map(ord, s))

    def hash(i):
        return ((i + magicoffset) * superprime) % supermod

    cmap = plt.cm.get_cmap(matplotlib_color_map_name)

    r = hash(str2int(s)) / supermod
    return cmap(r)


def legend_without_duplicate_labels(ax=None):
    """Same as `ax.legend()`, but ignores duplicate labels."""

    if ax is None:
        ax = plt.gca()
    handles, labels = ax.get_legend_handles_labels()
    ct = lambda h: tuple(h.get_facecolor()[0])
    unique = [(h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i] or ct(h) not in map(ct, handles[:i])]
    ax.legend(*zip(*unique))


def save_figure_for_latex(filename, reset_size=True):
    """Slaat het laatste gebruikte `figure` (waar alle `Axes` in zitten) op als .pdf. De grootte van de figure wordt veranderd naar een standaardgrootte."""
    fig = plt.gcf()

    if reset_size:
        fig.set_size_inches((8, 5))
    if not filename.endswith(".pdf"):
        filename = filename + ".pdf"

    fig.savefig(filename)

    if "/" not in filename:
        filename = "/notebooks/" + filename
    print("Saved to "+filename)


def save_figure_for_google_slides(filename, reset_size=True, dpi=600):
    """Slaat het laatste gebruikte `figure` (waar alle `Axes` in zitten) op als .png. De grootte van de figure wordt veranderd naar een standaardgrootte."""
    fig = plt.gcf()

    if reset_size:
        fig.set_size_inches((8, 5))
    if not filename.endswith(".png"):
        filename = filename + ".png"

    fig.savefig(filename, dpi=dpi)

    if "/" not in filename:
        filename = "/notebooks/" + filename
    print("Saved to "+filename)
