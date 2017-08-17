import matplotlib.pyplot as plt

DEFAULT_SHOW = True
DEFAULT_SAVE = False

# Accuracy-Robustness plot described in the paper of VOT
def _ar_plot(score):
    # Get the target target (video or dataset) name
    target_name = score.target_name
    # The filename for saving
    filename = 'ARPlot-{}.png'.format(target_name)
    # The data for painting
    result = score.results['ar_plot']
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

    plt.legend(loc = 'upper left')

    return fig, filename

# Success plot described in the paper of OTB
def _success_plot(score):
    # Get the target target (video or dataset) name
    target_name = score.target_name
    # The filename for saving
    filename = 'SucessPlot-{}.png'.format(target_name)
    # The data for painting
    result = score.results['success_plot']

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
        plt.plot(values['success_rates'], values['thresholds'], label = '{} [ {:.3f} ]'.format(tracker_name, values['auc']))
        plt.legend()

    return fig, filename

def plot(scores, show = DEFAULT_SHOW, save = DEFAULT_SAVE):
    for score in scores:
        for metric_name in score.get_metrics():
            if metric_name == 'success_plot':
                fig, filename = _success_plot(score)
            elif metric_name == 'ar_plot':
                fig, filename = _ar_plot(score)
            else:
                raise ValueError('Metric "{}" is not supported'.format(metric))

            # Save the plot as an image
            if save:
                plt.savefig(filename)

            # Show the plot
            if show:
                print 'Press ctrl + w or cmd + w to continue'
                plt.show()

            # Close the plot figure
            plt.close(fig)
