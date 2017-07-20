import matplotlib.pyplot as plt

DEFAULT_SHOW = True
DEFAULT_SAVE = False

def plot(score, show = DEFAULT_SHOW, save = DEFAULT_SAVE):
    for metric_name in score.get_metrics():
        if metric_name == 'success_plot':
            success_plot(score, show, save)
        else:
            # TODO
            '''Handle non-existed metric'''

# Success plot described in the paper of OTB
def success_plot(score, show = DEFAULT_SHOW, save = DEFAULT_SAVE):
    target_name = score.target_name
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

    # Save the plot as an image
    if save:
        filename = 'SucessPlot-{}.png'.format(target_name)
        plt.savefig(filename)

    # Show the plot
    if show:
        print 'Press ctrl + w or cmd + w to continue'
        plt.show()

    # Close the plot figure
    plt.close(fig)
