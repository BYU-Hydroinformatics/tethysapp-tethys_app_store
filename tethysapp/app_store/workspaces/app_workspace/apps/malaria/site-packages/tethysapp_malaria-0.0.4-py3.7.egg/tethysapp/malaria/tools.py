def definecurrentrisks():
    """
    reads the most recent csv and creates a dictionary of the form {ubigeo#: risk}
    """
    import pandas
    import os
    from .app import Malaria as App

    path = App.get_app_workspace().path
    path = os.path.join(path, 'output.csv')

    df = pandas.read_csv(path)[['epiweek']]
    last = df.max()[0]
    df = pandas.read_csv(path)[['ubigeo', 'epiweek', 'risk']]
    df = df.query("epiweek == @last")

    risk = {}
    for row in df.iterrows():
        risk[int(row[1][0])] = row[1][2]
    return risk


def historicalriskplot(ubigeo):
    """
    creates the historic risk highcharts dataset for the ubigeo argument
    """
    import pandas
    import os
    from .app import Malaria as App

    path = App.get_app_workspace().path
    path = os.path.join(path, 'output.csv')

    df = pandas.read_csv(path)[['ubigeo', 'epiweek', 'risk']]
    df = df.query("ubigeo == @ubigeo")
    first = df['epiweek'].min()
    last = df['epiweek'].max()

    # you have to manually make everything an integer because the numpy.int64 type is not json serializable
    chartdata = {'ubigeo': ubigeo, 'historical': [], 'epiweek': int(last)}

    for row in df.iterrows():
        chartdata['historical'].append([int(row[1][1]), row[1][2]])

    return chartdata
