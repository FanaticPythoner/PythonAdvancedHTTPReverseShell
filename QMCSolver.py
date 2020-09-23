import pandas as pd
from itertools import product, combinations
from copy import deepcopy
import numpy as np
import os


class QMCSolver:
    """
        Quine-McCluskey solver class

            Parameters:
                1. lstTrue: List of indices of values that needs to be equal to 1 in the truth table
                2. lstDontCare: List of indices of values that needs to be equal to "Don't care" (X) in the truth table
                3. lstVars: List of variables to use
                4. outputPath: Output excel path
                5. lang: language for the excel export. Can be either "en" (English) or "fr" (French)
    """
    def __init__(self, lstTrue, lstDontCare, lstVars, outputPath, lang="en"):
        self.lang = lang
        self.dicVars = {val:False for val in lstVars}
        self.lstVars = lstVars
        self.lstTrue = lstTrue
        self.lstDontCare = lstDontCare
        self.lstCalculations = []
        self.outputPath = outputPath
        os.makedirs(os.sep.join(self.outputPath.split(os.sep)[:-1]), exist_ok=True)
        self.truthTable = None
        self.writer = None
        self._getWriter()
        

        self.dicFunc = {}
        params = ''
        strBu = ""
        for var in lstVars:
            params = params + var + ','
            strBu = strBu + var + ' or '

        params = params[:-1]
        strBu = strBu[:-4]

        exec("def " + self._getResultLang() + "(" + params + "): return " + strBu, self.dicFunc)

        self._getTruthTable()


    def _getResultLang(self):
        """
            Get the traduction for the Result field
        
            RETURNS -> Str: string
        """
        if self.lang == "fr":
            return "Resultat"
        else:
            return "Result"


    def _getUsedLang(self):
        """
            Get the traduction for the Used field
        
            RETURNS -> Str: string
        """
        if self.lang == "fr":
            return "Utilise"
        else:
            return "Used"


    def _getNbBitsSectionLang(self):
        """
            Get the traduction for the "Bits Count / Section" field
        
            RETURNS -> Str: string
        """
        if self.lang == "fr":
            return "Nombre De Bits / Section"
        else:
            return "Bits Count / Section"


    def _getSelectFinalLang(self):
        """
            Get the traduction for the "Final Selection" field
        
            RETURNS -> Str: string
        """
        if self.lang == "fr":
            return "Sélection Finale"
        else:
            return "Final Selection"


    def _getFinalEqLang(self):
        """
            Get the traduction for the "Final Equation" field
        
            RETURNS -> Str: string
        """
        if self.lang == "fr":
            return "Équation Finale"
        else:
            return "Final Equation"


    def _getStepLang(self):
        """
            Get the traduction for the Step field
        
            RETURNS -> Str: string
        """
        if self.lang == "fr":
            return "Étape"
        else:
            return "Step"


    def _getStepCompLang(self):
        """
            Get the traduction for the "Comparison Step" field
        
            RETURNS -> Str: string
        """
        if self.lang == "fr":
            return "Étape De Comparaison"
        else:
            return "Comparison Step"


    def _getNoLang(self):
        """
            Get the traduction for the No field
        
            RETURNS -> Str: string
        """
        if self.lang == "fr":
            return "Non"
        else:
            return "No"


    def _getYesLang(self):
        """
            Get the traduction for the Yes field
        
            RETURNS -> Str: string
        """
        if self.lang == "fr":
            return "Oui"
        else:
            return "Yes"


    def _getTruthTableLang(self):
        """
            Get the traduction for the "Truth Table" field
        
            RETURNS -> Str: string
        """
        if self.lang == "fr":
            return "Table De Verite"
        else:
            return "Truth Table"


    def _getWriter(self):
        """
            Init the base ExcelWriter object
        
            RETURNS -> Void
        """
        self.writer = pd.ExcelWriter(self.outputPath, engine='xlsxwriter', options={'strings_to_numbers': True})
        self._addSheetWriter(self._getTruthTableLang())


    def _addSheetWriter(self, name):
        """
            Add an excel sheet by name to the current writer
        
            RETURNS -> Void
        """
        workbook=self.writer.book
        worksheet=workbook.add_worksheet(name)
        self.writer.sheets[name] = worksheet


    def _updateDataSheetWriter(self, name, df, index=True):
        """
            Update a given excel sheet to use a given dataframe
        
            RETURNS -> Void
        """
        df.to_excel(self.writer, sheet_name=name, index=index)


    def _getTruthTable(self):
        """
            Get the base truth table used to perform the Quine-McCluskey algorithm
        
            RETURNS -> Void
        """
        def truth_table(f):
            values = [list(x) + [f(*x)] for x in product([False,True], repeat=f.__code__.co_argcount)]
            return pd.DataFrame(values,columns=(list(f.__code__.co_varnames) + [f.__name__]))
            
        df = truth_table(self.dicFunc[self._getResultLang()])
        df[self._getResultLang()] = False

        df.iloc[self.lstTrue, df.columns.get_loc(self._getResultLang())] = 1
        df.iloc[self.lstDontCare, df.columns.get_loc(self._getResultLang())] = np.nan

        df = df.astype(float)
        df = df.replace(np.nan, 'X')
        df = df.astype(str).replace('1.0', '1').replace('0.0', '0')
        #df.to_excel(os.path.join(self.outputPath, 'Table_De_Verite.xlsx'), engine='xlsxwriter')
        self.truthTable = df.copy()
        self._updateDataSheetWriter(self._getTruthTableLang(), self.truthTable)
        #return df.copy()


    def _getNbBitsRow(self, row):
        """
            Get the number of bits in a given row

            RETURNS -> Int: lenConc
        """
        conc = row.to_frame().astype(str).values.sum(axis=1).tolist()
        conc = ''.join(conc)
        conc = conc.replace('0', '')
        return len(conc)


    def _getNbBitsDf(self):
        """
            Get the number of bits for each row in the current self.truthTable dataframe
        
            RETURNS -> DataFrame: dfNbBits
        """
        dfNbBits = self.truthTable.copy()
        cols = [dfNbBits.columns.get_loc(val) for val in dfNbBits.columns.values.tolist() if val != self._getResultLang()]
        dfCount = dfNbBits.iloc[:, cols].apply(lambda x: self._getNbBitsRow(x), axis=1)
        dfNbBits[self._getNbBitsSectionLang()] = dfCount
        return dfNbBits


    def _getMulitpleDfBitsCount(self, df):
        """
            Split a given dataset into multiple dataset from its BitsCount
        
            RETURNS -> List: dfLst
        """
        df[self._getUsedLang()] = False
        uniqueVals = df[self._getNbBitsSectionLang()].unique()
        dfLst = []

        for val in uniqueVals:
            resLang = self._getResultLang()
            dfFound = df.query('`' + self._getNbBitsSectionLang() + '` == ' + str(val) + ' and ' + resLang + ' != "0"').copy().reset_index(drop=True)
            dfLst.append(dfFound)

        return dfLst


    def _getPosUnderscodeStr(self, conc):
        """
            Get all the positions of the underscores in a string
        
            RETURNS -> List: underscoresIndices
        """
        return [i for i, ltr in enumerate(conc) if ltr == '_']


    def _getStringFromSerie(self, serie, skipResultat=False):
        """
            Transform a serie into a string (using provided variables only)
        
            RETURNS -> Str: conc
        """
        toFrame = serie.to_frame()

        if not skipResultat:
            toFrame = toFrame.iloc[[val for val in range(len(toFrame) - 3)], :]
        else:
            toFrame = toFrame.iloc[[val for val in range(len(toFrame) - 2)], :]

        conc = toFrame.astype(str).values.sum(axis=1).tolist()
        conc = ''.join(conc)
        return conc


    def _getPosIndexDiffStr(self, str1, str2, forceArray=False):
        """
            Get all the differences between two strings

            RETURNS -> (List/Int: diff, Int: nbDiff)
        """
        diff = None
        nbDiff = 0
        for i, val1 in enumerate(str1):
            if val1 != str2[i]:

                if not forceArray:
                    if diff is None:
                        diff = i
                else:
                    if diff is None:
                        diff = []
                    diff.append(i)

                nbDiff = nbDiff + 1

        return (diff, nbDiff)


    def _getNotUsed(self, dfsBitCount):
        """
            Get all the non-used rows for the current Quine-McCluskey step

            RETURNS -> List: [Int: iLstDf, Int: iRowDf]
        """
        notUsed = []
        for i in range(len(dfsBitCount)):
            df1 = dfsBitCount[i]
            for i1, row1 in df1.iterrows():
                used = df1.iloc[i1, df1.columns.get_loc(self._getUsedLang())]
                if not used:
                    notUsed.append([i, i1])

        return notUsed


    def _getBaseDict(self):
        """
            Get the base empty dictionnary for DataFrame creation

            RETURNS -> Dict : d
        """
        d = {val:[] for val in self.lstVars}
        d[self._getResultLang()] = []
        d[self._getNbBitsSectionLang()] = []
        d[self._getUsedLang()] = []
        return d



    def _getStep(self, dfsBitCount, numStep):
        """
            Calculate a current step for the Quine-McCluskey

            RETURNS -> (Bool : canContinue, DataFrame : currDf, DataFrame : currDfPrint, DataFrame : starsDf)
        """
        def _dropDuplicates(currDf):
            cols = [currDf.columns.get_loc(val) for val in currDf.columns.values.tolist() if val not in (self._getResultLang())]
            dfCopy = currDf.iloc[:, cols].copy()
            dfCopy.drop_duplicates(inplace=True)
            currDf = currDf.iloc[dfCopy.index.values.tolist(), :].copy()
            return currDf.reset_index(drop=True)


        def _updateCurrDfVal(currDf, row):
            newRow = {}
            for i, col in enumerate(row.index):
                newRow[col] = row.iloc[i, :]

            newRow = pd.DataFrame(newRow)
            currDf = pd.concat([currDf, newRow], axis=0)
            return currDf.reset_index(drop=True)
            

        currDf = pd.DataFrame(self._getBaseDict())
        starsDf = self._getBaseDict()
        canContinue = True
        
        for i in range(0, len(dfsBitCount) - 1):
            if len(dfsBitCount) % 2 != 0 and i == len(dfsBitCount) - 1:
                for iRow, row in dfsBitCount[i].iterrows():
                    for val in self.lstVars:
                        starsDf[val].append(row[val])
                break


            df1 = dfsBitCount[i]
            df2 = dfsBitCount[i + 1]

            nbBits = i + 1

            for i2, row2 in df2.iterrows():
                strRow2 = self._getStringFromSerie(row2)
                undStr2 = self._getPosUnderscodeStr(strRow2)

                for i1, row1 in df1.iterrows():
                    strRow1 = self._getStringFromSerie(row1)
                    undStr1 = self._getPosUnderscodeStr(strRow1)
                    undStr1Len = len(undStr1)

                    underscoreOk = False

                    if undStr1Len > 0:
                        if undStr1 == undStr2:
                            underscoreOk = True
                        else:
                            s = 0
                    else:
                        underscoreOk = True

                    if underscoreOk:
                        posDiff, nbDif = self._getPosIndexDiffStr(strRow1, strRow2)

                        if nbDif == 1:
                            row2Frame = row2.to_frame().copy()
                            indexNbBits = row2Frame.index.values.tolist().index(self._getNbBitsSectionLang())
                            indexUtilise = row2Frame.index.values.tolist().index(self._getUsedLang())
                            row2Frame.iloc[posDiff, :] = '_'
                            row2Frame.iloc[indexNbBits, :] = nbBits
                            row2Frame.iloc[indexUtilise, :] = True
                            currDf = _updateCurrDfVal(currDf, row2Frame)
                            dfsBitCount[i].iloc[i1, df1.columns.get_loc(self._getUsedLang())] = True
                            dfsBitCount[i + 1].iloc[i2, df2.columns.get_loc(self._getUsedLang())] = True
                
        currDf = _dropDuplicates(currDf)
        notUsed = self._getNotUsed(dfsBitCount)
        nbBits = 1
        lastIndex = notUsed[0][0] if len(notUsed) > 0 else -1
        for i, i1 in notUsed:
            if i != lastIndex:
                lastIndex = i
                nbBits = nbBits + 1

            for val in self.lstVars:
                starsDf[val].append(dfsBitCount[i].iloc[i1, dfsBitCount[i].columns.get_loc(val)])

            starsDf[self._getResultLang()] = dfsBitCount[i].iloc[i1, dfsBitCount[i].columns.get_loc(self._getResultLang())]
            starsDf[self._getNbBitsSectionLang()] = nbBits #dfsBitCount[i].iloc[i1, dfsBitCount[i].columns.get_loc(self._getNbBitsSectionLang())]
            starsDf[self._getUsedLang()] = dfsBitCount[i].iloc[i1, dfsBitCount[i].columns.get_loc(self._getUsedLang())]


        starsDf = pd.DataFrame(starsDf)
        canContinue = len(currDf) != 0

        currDfPrint = currDf
        if canContinue:
            cols = [currDf.columns.get_loc(val) for val in currDf.columns.values.tolist() if val not in (self._getResultLang())]
            currDfPrint = currDf.iloc[:, cols].copy()#.replace(False, self._getNoLang()).replace(True, self._getYesLang())
            #if len(notUsed) > 0:
            #    currDfPrint.iloc[[y for x,y in notUsed], currDfPrint.columns.get_loc(self._getUsedLang())] = self._getNoLang()
            # currDf = currDf.iloc[:, cols].copy()
            currDf = self._getMulitpleDfBitsCount(currDf)

        return (canContinue, currDf, currDfPrint, starsDf)



    def _getFinalStep(self, dfStarsComp):
        """
            Create the Quine-McCluskey comparison table used for the final equation

            RETURNS -> DataFrame : dfObj
        """
        cols = self.truthTable.query('' + self._getResultLang() + ' == "1"')
        cols = cols.iloc[:, [val for val in range(cols.shape[1] - 1)]]
        cols = [col.astype(str).values.sum(axis=0) for i, col in cols.iterrows()]
        index = [self._getStringFromSerie(ind) for i, ind in dfStarsComp.iterrows()]
        dfObj = pd.DataFrame(data=np.zeros((len(index), len(cols))), columns=cols, index=index)

        lstValide = []

        for iCol, col in enumerate(cols):
            for iRow, row in enumerate(index):
                undsRow = self._getPosUnderscodeStr(row)
                posDiff, nbDif = self._getPosIndexDiffStr(row, col, forceArray=True)
                for undIndex in undsRow:
                    if str(posDiff).isdigit():
                        if undIndex == posDiff:
                            posDiff = []
                            nbDif = nbDif - 1
                    else:
                        if undIndex in posDiff:
                            posDiff.remove(undIndex)
                            nbDif = nbDif - 1
                
                if nbDif == 0:
                    lstValide.append((iRow, iCol))

        for iRow, iCol in lstValide:
            dfObj.iloc[iRow, iCol] = 1

        dfObj[self._getSelectFinalLang()] = self._getNoLang()
        cols = [x for x in dfObj.columns.values.tolist() if x != self._getSelectFinalLang()]#dfObj.columns.get_loc(x)
        bestRows = self._getBestRowsFinalSelection(dfObj, cols) #dfObj.loc[:, cols][dfObj.sum(axis=1).ge(2)]
        dfObj.loc[bestRows.index.values.tolist(), [self._getSelectFinalLang()]] = self._getYesLang()

        nameSheet = self._getStepCompLang()
        self._addSheetWriter(nameSheet)
        self._updateDataSheetWriter(nameSheet, dfObj)

        return dfObj


    def _getBestRowsFinalSelection(self, df, cols):
        """
            Get the selected rows for the final selection

            RETURNS -> DataFrame : dfSelected
        """
        isOne = df.loc[df[df.loc[:, cols] == 1].sum(axis=1) > 0, :]
        lstIsOne = isOne.loc[:, cols].values.tolist()
        lstIsOne = [(x, lstItem) for x, lstItem in zip(isOne.index.values.tolist(), lstIsOne)]
        winningComb = None
        stopFlag = False

        for i in range(1, isOne.shape[0] + 1):
            if stopFlag:
                break;
            combs = combinations(lstIsOne, i)

            for c in combs:
                data = [x[1] for x in c]
                index = [x[0] for x in c]
                dfTmp = pd.DataFrame(data=data, columns=cols, index=index)
                if (dfTmp.sum() > 0).all():
                    dfTmp[self._getSelectFinalLang()] = self._getYesLang()
                    winningComb = dfTmp
                    stopFlag = True
                    break;


        return winningComb



    def _getFinalEquation(self, dfObj):
        """
            Get and save the final equation found after doing the Quine-McCluskey

            RETURNS -> Void
        """
        strEq = ""
        rows = dfObj.query('`' + self._getSelectFinalLang() + '` == "' + self._getYesLang() + '"')
        for head in rows.index.values.tolist():
            for i, char in enumerate(head):
                if char == "1":
                    strEq = strEq + self.lstVars[i]
                elif char == "0":
                    strEq = strEq + "(-" + self.lstVars[i] + ")"

            strEq = strEq + " + "

        finalEqLang = self._getFinalEqLang()
        strEq = pd.DataFrame({
           finalEqLang : [strEq[:-3]]
        })
        
        nameSheet = finalEqLang
        self._addSheetWriter(nameSheet)
        self._updateDataSheetWriter(nameSheet, strEq, index=False)



    def calculate(self):
        """
            Calculate the whole Quine-McCluskey

            RETURNS -> Void
        """
        df = self._getNbBitsDf()
        dfsBitCount = self._getMulitpleDfBitsCount(df)

        currDfPrint = pd.concat(dfsBitCount, axis=0)
        currDfPrint[self._getUsedLang()] = self._getYesLang()
        cols = [currDfPrint.columns.get_loc(val) for val in currDfPrint.columns.values.tolist() if val not in (self._getResultLang())]
        currDfPrint = currDfPrint.iloc[:, cols].copy().reset_index(drop=True)#.replace(False, self._getNoLang()).replace(True, self._getYesLang())

        nameSheet = self._getStepLang() + ' 1'
        self._addSheetWriter(nameSheet)
        self._updateDataSheetWriter(nameSheet, currDfPrint)

        numStep = 2
        canContinue = True
        starsDf = pd.DataFrame(self._getBaseDict())
        dfStarsComp = starsDf.copy()

        lstDfPrint = []

        while canContinue:
            canContinue, dfsBitCount, currDfPrint, starsDf = self._getStep(dfsBitCount, numStep)

            if not canContinue:
                lstDfPrint[-1][self._getUsedLang()] = self._getNoLang()
                if lstDfPrint[-1].shape[0] != starsDf.shape[0]:
                    raise Exception('Marche pas, pas la même taille pour dernière itération')
                # cols = [starsDf.columns.get_loc(val) for val in starsDf.columns.values.tolist() if val not in (self._getResultLang())]
                # starsDf = starsDf.iloc[:, cols].copy().reset_index(drop=True).replace(False, self._getNoLang()).replace(True, self._getYesLang())
                # starsDf.iloc[:, starsDf.columns.get_loc(self._getUsedLang())] = self._getNoLang()
                # nameSheet = self._getStepLang() + ' ' + str(numStep - 1)
                # self._addSheetWriter(nameSheet)
                # self._updateDataSheetWriter(nameSheet, starsDf)
                # lstDfPrint[-1] = starsDf
            else:
                if len(starsDf) > 0:
                    for iStar, starRow in starsDf.iterrows():
                        for i, row in lstDfPrint[-1][::-1].iterrows():
                            strRow1 = self._getStringFromSerie(row, skipResultat=True)
                            strRow2 = self._getStringFromSerie(starRow)
                            if strRow1 == strRow2:
                                lstDfPrint[-1].iloc[i, lstDfPrint[-1].columns.get_loc(self._getUsedLang())] = self._getNoLang()
                                break

                lstDfPrint.append(currDfPrint)

            dfStarsComp = pd.concat([dfStarsComp, starsDf], axis=0)
            numStep = numStep + 1

        numStep = 2
        for dataf in lstDfPrint:
            dataframe = dataf.copy()
            dataframe[self._getUsedLang()] = dataframe[self._getUsedLang()].replace(True, self._getYesLang())
            nameSheet = self._getStepLang() + ' ' + str(numStep)
            try:
                self._addSheetWriter(nameSheet)
            except Exception as e:
                pass
            self._updateDataSheetWriter(nameSheet, dataframe)
            numStep = numStep + 1

        
        dfObj = self._getFinalStep(dfStarsComp)

        self._getFinalEquation(dfObj)

        self.writer.save()
