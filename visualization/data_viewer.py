from calibration_analyzer import adjuster
import core.metnl as metnl
import os
import datetime
from calibration_analyzer.exam_class import TimeSeries
from matplotlib import pyplot as plt


def panel_update(params: dict):
    datafile = params["data_path@filepath"]
    channel = params["channel@int"]
    if not os.path.isfile(datafile):
        print(f"File {datafile} is not exists, cancaling...")
        return
    try:
        timeSeries = TimeSeries.load_multichannel_from_binary(datafile)
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    data1 = timeSeries[channel]
    data1.plot(clear=True)
    plt.show()


def main():
    initial_params = {
        "data_path@filepath": '',
        "channel@int": 0
    }
    panel = adjuster.Panel(initial_params, panel_update,
                           name="Time Series Viewer")
    panel_update(initial_params)
    return panel

if __name__ == "__main__":
    main()
