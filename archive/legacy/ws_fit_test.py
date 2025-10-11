from calibration_analyzer import exam_process
from calibration_analyzer import exam_class
import matplotlib.pyplot as plt


ws = exam_class.System.loadFile(
    "data\M50\output_20241022_164246_MTSS1_ws_A16_震级5.0_analyze.json")
ws_fit = exam_process.ws_system_fit(ws, direct_guess=True)

ws.plot()
ws_fit.plot()
plt.show()
