from QMCSolver import QMCSolver


lstVars = ['A', 'B', 'C', 'D']
lstTrue = [1, 3, 13, 15]
lstDontCare = [0, 2, 8, 10, 11]
outputPath = r'Output\Result.xlsx'

cl = QMCSolver(lstTrue, lstDontCare, lstVars, outputPath)
cl.calculate()