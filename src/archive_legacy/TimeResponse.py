from calibration_analyzer.exam_class import System
from matplotlib import pyplot as plt
from IIR_LNRNN import IIR_LRNN

if __name__ == "__main__":
    # Create a system object
    s = System.s
    # second order system
    sys = System.fromSymbol((s + 1) / (s**2 + 2*s + 1))
    sys.plot()
    sys_time = sys.frequency_response_system()
    sys_time.plot()
    lrnn = IIR_LRNN.fromSystem(sys, fs=2000)
    lrnn_time = lrnn.frequency_response_system()
    lrnn_time.plot()
    plt.show()
