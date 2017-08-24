import matplotlib.pyplot as plt, mpld3
import pandas as pd
from trkrutils import webapp

DEFAULT_SHOW = True
DEFAULT_SAVE = False

DEFAULT_TABLE_ORDER = [
    'ACC',
    'ROB',
    'AUC',
    'PREC'
]

# Generate a table for given value name from a result
def _gen_table(result, value_name, shown_name):
    tracker_names = []
    tracker_values = []

    # Find the corresponding value for each tracker
    for tracker_name, values in result.iteritems():
        tracker_names.append(tracker_name)
        tracker_values.append(values[value_name])

    table = pd.DataFrame(data = tracker_values, columns = [shown_name], index = tracker_names)

    return table

# Accuracy-Robustness plot described in the paper of VOT
def _ar_plot(score):
    # Get the target target (video or dataset) name
    target_name = score.target_name
    # The filename for saving
    filename = 'ARPlot-{}.png'.format(target_name)
    # The data for painting
    result = score.results['ar_plot']
    # Generate the table for this metric
    acc_table = _gen_table(result, 'accuracy', 'ACC')
    rob_table = _gen_table(result, 'reliability', 'ROB')
    table = pd.concat([acc_table, rob_table], axis = 1)
    # The sensitivity
    # XXX: We assume at least one tracker is measured and all trackers are measured under the same sensitivity
    sensitivity = result.values()[0]['sensitivity']

    # Create a new plot figure
    fig = plt.figure()

    # Fill the fixed text
    plt.xlabel('Robustness (S = {})'.format(sensitivity))
    plt.ylabel('Accuracy')
    plt.title('Accuracy-Robustness plot of {}'.format(target_name))
    plt.axis([0, 1, 0, 1])
    plt.grid()

    # Fill the score for each tracker
    for tracker_name, values in result.iteritems():
        plt.scatter(x = values['reliability'], y = values['accuracy'], label = '{}'.format(tracker_name))

    # TODO:
    # For mpld3, the markers for plt.scatter do not appear in legends. We should find
    # out how to fix the bug.
    # mpld3 missing features: https://github.com/mpld3/mpld3/wiki#mpld3-missing-features
    plt.legend(loc = 'upper left')

    return fig, table, filename

# Success plot described in the paper of OTB
def _success_plot(score):
    # Get the target target (video or dataset) name
    target_name = score.target_name
    # The filename for saving
    filename = 'SucessPlot-{}.png'.format(target_name)
    # The data for painting
    result = score.results['success_plot']
    # Generate the table for this metric
    table = _gen_table(result, 'auc', 'AUC')

    # Create a new plot figure
    fig = plt.figure()

    # Fill the fixed text
    plt.ylabel('Success rate')
    plt.xlabel('Overlap threshold')
    plt.title('Success plot of {}'.format(target_name))
    plt.axis([0, 1, 0, 1])
    plt.grid()

    # Fill the score for each tracker
    for tracker_name, values in result.iteritems():
        plt.plot(values['thresholds'], values['success_rates'], label = '{} [ {:.3f} ]'.format(tracker_name, values['auc']))
        plt.legend()

    return fig, table, filename

# Precision plot described in the paper of OTB
def _precision_plot(score):
    # Get the target target (video or dataset) name
    target_name = score.target_name
    # The filename for saving
    filename = 'PrecisionPlot-{}.png'.format(target_name)
    # The data for painting
    result = score.results['precision_plot']
    # Generate the table for this metric
    table = _gen_table(result, 'precision_score', 'PREC')
    # Get the maximum threshold
    # XXX:
    # We assume at least one tracker result is in the score and all trackers are evaluated under same max threshold
    max_threshold = result.itervalues().next()['max_threshold']

    # Create a new plot figure
    fig = plt.figure()

    # Fill the fixed text
    plt.ylabel('Precision')
    plt.xlabel('Location error threshold')
    plt.title('Precision plot of {}'.format(target_name))
    plt.axis([0, max_threshold, 0, 1,])
    plt.grid()

    # Fill the score for each tracker
    for tracker_name, values in result.iteritems():
        plt.plot(values['thresholds'], values['precisions'], label = '{} [ {:.3f} ]'.format(tracker_name, values['precision_score']))

    # Paint the legend
    plt.legend()

    return fig, table, filename

def report(scores, show = DEFAULT_SHOW, save = DEFAULT_SAVE):
    data_list = []

    for score in scores:
        html_plots = []
        table = pd.DataFrame()

        for metric_name in score.get_metrics():
            if metric_name == 'success_plot':
                fig, _table, filename = _success_plot(score)
            elif metric_name == 'precision_plot':
                fig, _table, filename = _precision_plot(score)
            elif metric_name == 'ar_plot':
                fig, _table, filename = _ar_plot(score)
            else:
                raise ValueError('Metric "{}" is not supported'.format(metric))

            # Save the plot as an image
            if save:
                plt.savefig(filename)

            # Append the plot and table for showing
            if show:
                html_plots.append(mpld3.fig_to_html(fig))
                table = pd.concat([table, _table], axis = 1)

            # Close the plot figure
            plt.close(fig)

        if show:
            # Reorder the table
            table_order = [x for x in DEFAULT_TABLE_ORDER if x in table.columns.values]
            table = table[table_order]
            table = table.sort_values(table.columns[0], ascending = False)
            # Append the data for showing
            data_list.append({
                'name': score.target_name,
                'type': score.target_type,
                'html_plots': html_plots,
                'table': table
            })

    if show:
        webapp.run(data_list)
