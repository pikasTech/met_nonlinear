from .met import exam_process, exam_class
from . import met

def assert_num(a, b, num=0.0001):
    assert abs(a - b) < num

def common_exam_process(single_sheet=304):
    exam = exam_process.Exam()
    exam.config.get_data_from_xlsx = 1
    exam.config.sheetList = [single_sheet]
    exam.config.WfType = 1
    exam.config.hand_data = single_sheet
    exam.config.dataLength = 30
    exam.config.isAutoDataLength = 0
    exam.config.fitRange = range(5, 25)
    exam.config.fl = 0.7
    exam.config.xlsxDir = '../met/met_data/main_data.xlsx'  # 原始数据的xlsx路径

    T1 = 1 / 70
    bet = 1 / 5 / T1
    T2 = 1 / 50
    alp = 1 / 200 / T1
    exam.config.Wp = exam_class.System()
    exam.config.Wp.T1 = T1
    exam.config.Wp.bet = bet
    exam.config.Wp.T2 = T2
    exam.config.Wp.alp = alp

    return exam

def test_case1():
    exam = common_exam_process()

    exam.process()
    assert abs(exam.res.Kp0 - 0.13150453891072927) < 0.0001
    assert abs(exam.res.Kd0 - 0.08617647328700018) < 0.0001

    assert exam.res.Wfb0_simply.abs.all() == exam.res.Wfb0_kpkd.abs.all()

def test_case2():
    exam = common_exam_process()

    exam.process()
    exam.save()
    # Add any necessary assertions or validations for test_case2
    data = met.loadData()
    print(data)
    assert_num(data.fit.A, 30031358.10167074)
    assert_num(data.fit.B, 387416559.39261514)
    assert_num(data.fit.C, 1651255.9087461387)
    assert_num(data.fit.simu_C_14, 7.75169707478518e-06)
    assert_num(data.fit.simu_C_15, 2.1311116790347687e-07)
    assert_num(data.fit.simu_C_16, 1.2111992995190406e-10)

if __name__ == '__main__':
    test_case2()
