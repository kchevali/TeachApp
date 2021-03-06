# from sklearn import linear_model
from base_models import Classifier, Regression, SVMBase
from sklearn import metrics
from scipy import spatial
import numpy as np
import helper as hp
from graphics import Points, HStack
from math import inf, sqrt, log, e
# from random import uniform


class DecisionTree(Classifier):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.graphics.append(Points(pts=self.getCircleLabelPts(), color=self.color, isConnected=False))

    def setTable(self, **kwargs):
        super().setTable(**kwargs)
        self.curr = DTNode(table=self.table)

    def getTable(self):
        return self.curr.table

    def getChildren(self):
        return self.curr.children

    def getParent(self):
        return self.curr.parent

    def getParentColumn(self):
        return self.curr.parent.colIndex

    def getParentColName(self):
        return self.curr.parent.getColName()

    def getColName(self):
        return self.curr.getColName()

    def getValue(self):
        return self.curr.value

    def isVertical(self):
        return type(self.getView().keyDown("div")) != HStack

    def add(self, colIndex):
        self.curr.setCol(colIndex)

    def remove(self):
        self.curr.reset()

    def goBack(self):
        self.curr = self.curr.parent

    def go(self, index):
        self.curr = self.curr.children[index]

    def predict(self, row):
        return self.curr.predict(row)

    def modelPredict(self, row):
        return self.predict([row])[0]

    def modelTest(self, testData):
        y_pred = self.predict(testData.encodedData)
        y_test = testData.targetCol
        return metrics.accuracy_score(y_test, y_pred)

    def isRoot(self):
        return self.curr and not self.curr.parent

    def hasChildren(self):
        return self.curr and len(self.curr.children) > 0

    def getChild(self, index):
        return self.curr.children[index]


class DTNode:

    def __init__(self, table, parent=None, value=None):
        self.table = table
        self.parent = parent
        self.value = value
        self.colIndex = None
        self.children = []
        # self.tree = tree

    def setCol(self, colIndex):
        self.colIndex = colIndex
        self.children = []
        for item in self.table.uniqueVals(self.colIndex):
            newTable = self.table.matchValue(colIndex=self.colIndex, value=item)
            self.children.append(DTNode(
                table=newTable,
                parent=self, value=item
            ))

    def reset(self):
        self.colIndex = None
        self.children = []

    def predict(self, x):
        # print("Row:", x)
        if len(self.children) > 0:
            for child in self.children:
                if child.value == x[self.colIndex]:
                    return child.predict(x)
            # return None
        # print("Majority:", self.table.majorityInTargetColumn())
        return self.table.majorityInTargetColumn()

    def getColName(self):
        return self.table.xNames[self.colIndex] if self.colIndex != None else None


class RandomForest(Classifier):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def setTable(self, **kwargs):
        super().setTable(**kwargs)
        self.curr = self.newTree()
        self.trees = []

    def newTree(self):
        return DecisionTree(table=self.table, testingTable=self.testingTable)

    def predict(self, _x):
        mostFreq = None
        predictions = {}
        predictions[mostFreq] = 0

        for tree in self.trees:
            p = tree.predict(_x)
            if(p in predictions):
                predictions[p] += 1
            else:
                predictions[p] = 1

            if predictions[p] > predictions[mostFreq]:
                mostFreq = p
        return mostFreq

    def saveTree(self):
        self.trees.append(self.curr)
        self.curr = self.newTree()

    def add(self, *args, **kwargs):
        return self.curr.add(*args, **kwargs)

    def getParent(self, *args, **kwargs):
        return self.curr.getParent(*args, **kwargs)

    def getChildren(self, *args, **kwargs):
        return self.curr.getChildren(*args, **kwargs)

    def getColName(self, *args, **kwargs):
        return self.curr.getColName(*args, **kwargs)

    def getChild(self, *args, **kwargs):
        return self.curr.getChild(*args, **kwargs)

    def remove(self, *args, **kwargs):
        return self.curr.remove(*args, **kwargs)

    def hasChildren(self, *args, **kwargs):
        return self.curr.hasChildren(*args, **kwargs)

    def go(self, *args, **kwargs):
        return self.curr.go(*args, **kwargs)

    def getParentColName(self, *args, **kwargs):
        return self.curr.getParentColName(*args, **kwargs)

    def getValue(self, *args, **kwargs):
        return self.curr.getValue(*args, **kwargs)

    def isRoot(self, *args, **kwargs):
        return self.curr.isRoot(*args, **kwargs)

    def goBack(self, *args, **kwargs):
        return self.curr.goBack(*args, **kwargs)

    def getTable(self, *args, **kwargs):
        return self.curr.getTable(*args, **kwargs)

    def __len__(self):
        return len(self.trees)


class KNN(Classifier):

    def __init__(self, k=3, bestK=False, **kwargs):
        self.k = k
        self.bestK = bestK
        super().__init__(displayRaw=True, **kwargs)

    def setTable(self, **kwargs):
        super().setTable(**kwargs)
        self.kdTree = spatial.KDTree(np.array(self.table.x))
        if self.bestK:
            self.findBestK(testTable=self.testingTable)

    def getNeighbor(self, _x):
        return np.reshape(self.kdTree.query(_x, k=self.k)[1], self.k)  # if type(_x) == np.ndarray else np.array(_x)

    def predict(self, _x):
        ys = np.array([self.table.y[i][0] for i in self.getNeighbor(_x)])
        # return np.argmax(np.bincount(ys))
        u, indices = np.unique(ys, return_inverse=True)
        return u[np.argmax(np.bincount(indices))]

    def findBestK(self, testTable):
        acc = self.accuracy(testTable=testTable)
        bestAcc = 0
        while(acc > bestAcc):
            self.k += 2
            bestAcc = acc
            acc = self.accuracy(testTable=testTable)
            if(acc <= bestAcc):
                self.k -= 2


class Linear(Regression):
    def __init__(self, n=1, alpha=1e-3, epsilon=1e-3, **kwargs):
        super().__init__(critPtCount=n + 1, isLinear=n == 1, **kwargs)
        self.n = n
        self.alpha = alpha
        self.epsilon = epsilon
        self.llamda = 0.1
        self.dJ = self.epsilon

    def reset(self):
        if "n" in self.__dict__:
            self.critPtCount = self.n + 1
        super().reset()

    def getEq(self):
        if len(self.critPts) > 0:
            x1, y1 = self.critPts[0]
            if len(self.critPts) > 1:
                x2, y2 = self.critPts[1]
                if self.n == 1 and x2 != x1:
                    self.getLinearEq(x1, y1, x2, y2)
                if len(self.critPts) > 2 and self.n == 2:
                    x3, y3 = self.critPts[2]
                    if x2 != x1 and x3 != x1 and x3 != x2:
                        self.getQuadEq(x1, y1, x2, y2, x3, y3)

    def getX(self, y):
        if self.n == 1:
            slope, intercept = tuple(self.cef)
            return (y - intercept) / slope if slope != 0 else inf
        elif self.n == 2:
            a, b, c = tuple(self.cef)
            delta = b * b - 4 * a * (c - y)
            # print("Y:", y, "Delta:", delta)
            if delta < 0 or a == 0:
                return None, None
            return (-b + sqrt(delta)) / (2 * a), (-b - sqrt(delta)) / (2 * a)

    def getY(self, x):
        y = 0
        x_ = 1
        for i in range(self.n, -1, -1):
            y += self.cef[i] * x_
            x_ *= x
        return y

    def getQuadEq(self, x1, y1, x2, y2, x3, y3):
        denom = (x1 - x2) * (x1 - x3) * (x2 - x3)
        a = (x3 * (y2 - y1) + x2 * (y1 - y3) + x1 * (y3 - y2)) / denom
        b = (x3 * x3 * (y1 - y2) + x2 * x2 * (y3 - y1) + x1 * x1 * (y2 - y3)) / denom
        c = (x2 * x3 * (x2 - x3) * y1 + x3 * x1 * (x3 - x1) * y2 + x1 * x2 * (x1 - x2) * y3) / denom
        self.cef = [a, b, c]

    def getLinearEq(self, x1, y1, x2, y2):
        slope = (y2 - y1) / (x2 - x1)
        intercept = y1 - slope * x1
        self.cef = [slope, intercept]

    def fit(self):
        if self.dJ >= self.epsilon:
            newCefs = [self.cef[i] - self.alpha * self.getJGradient(degreeX=self.n - i) for i in range(self.n + 1)]
            self.dJ = self.getJ(self.cef) - self.getJ(newCefs)
            self.cef = newCefs
            ptsGraphics = self.getGraphic("pts")
            if ptsGraphics != None:
                ptsGraphics.setPts(self.getPts())

            eqGraphics = self.getGraphic("eq")
            if eqGraphics != None:
                eqGraphics.setFont(text=self.getEqString())

            errGraphics = self.getGraphic("err")
            if errGraphics != None:
                errGraphics.setFont(text=self.getScoreString())
            return
        print("FIT DONE")
        self.isRunning = False

    def getJ(self, cef):
        total = 0
        # testTotal = 0
        for i in range(self.table.rowCount):
            localTotal = self.table.y[i][0]
            for j in range(self.n + 1):
                localTotal -= cef[j] * (self.table.x[i][0]**(self.n - j))

            # testTotal += (self.table.y[i] - cef[0] * self.table.x[i] - cef[1])**2
            total += localTotal * localTotal
        # print("J:", total, testTotal)
        return total

    def getJGradient(self, degreeX):
        total = 0
        # testTotal = 0
        for i in range(self.table.rowCount):
            localTotal = -self.table.y[i][0]
            for j in range(self.n + 1):
                localTotal += self.cef[j] * (self.table.x[i][0]**(self.n - j))
            total += localTotal * (self.table.x[i][0]**degreeX)
            # testTotal += (self.cef[0] * self.table.x[i] + self.cef[1] - self.table.y[i]) * (self.table.x[i]**degreeX)
        # print("G:", total, testTotal)
        total /= self.table.rowCount
        # print("Gradient Step:", total)
        return total

    def fitLasso(self):
        if self.dJ >= self.epsilon:
            newCefs = [self.cef[i] - self.alpha * self.getJGradient(degreeX=self.n - i) / self.table.rowCount for i in range(self.n + 1)]
            # a = self.cef[0] - self.alpha * self.getJGradient(multX=True) / self.table.rowCount
            # b = self.cef[1] - self.alpha * self.getJGradient(multX=False) / self.table.rowCount
            self.dJ = self.getJ(self.cef) - self.getJ(newCefs)
            self.cef = newCefs
            # print(self.cef, self.dJ)
            return True
        return False

    def getJLasso(self, cef):
        total = 0
        # testTotal = 0
        for i in range(self.table.rowCount):
            localTotal = self.table.y[i]
            for j in range(self.n + 1):
                localTotal -= cef[j] * (self.table.x[i]**(self.n - j))

            # testTotal += (self.table.y[i] - cef[0] * self.table.x[i] - cef[1])**2
            total += localTotal * localTotal
        for j in range(self.n + 1):
            total += abs(cef[j]) * self.llamda
        # print("J:", total, testTotal)
        return total

    def getJGradientLasso(self, degreeX):
        total = 0
        # testTotal = 0
        for i in range(self.table.rowCount):
            localTotal = -self.table.y[i]
            for j in range(self.n + 1):
                localTotal += self.cef[j] * (self.table.x[i]**(self.n - j))
            total += localTotal * (self.table.x[i]**degreeX)
            # testTotal += (self.cef[0] * self.table.x[i] + self.cef[1] - self.table.y[i]) * (self.table.x[i]**degreeX)
        for j in range(self.n + 1):
            total -= self.llamda * self.cef[j] / abs(self.cef[j])
        # print("G:", total, testTotal)
        return total

    def getEqString(self):
        out = "Y="
        n = self.n
        for i in range(self.n + 1):
            out += self.cefString(constant=self.cef[i], power=n, showPlus=i > 0, roundValue=4)
            n -= 1
        return out

    def getPts(self):
        return self.getLinearPts(isLinear=self.n == 1)


class Logistic(Regression):

    def __init__(self, **kwargs):
        super().__init__(critPtCount=2, isLinear=False, **kwargs)
        # self.compModel = linear_model.LogisticRegression()

    def getEq(self):
        if len(self.critPts) > 1:
            x1, y1 = self.critPts[0]
            x2, y2 = self.critPts[1]
            if x2 != x1:
                self.getSigmoidEq(x1, y1, x2, y2)

    # y = height / (1 + e^(ax+b))

    def invY(self, y):
        return log((1.0 - y) / y)  # * self.height

    def getX(self, y):
        return (self.invY(y) - self.cef[1]) / self.cef[0]

    def getY(self, x):
        try:
            exp = e**(x * self.cef[0] + self.cef[1])
            return (1.0 / (1.0 + exp))
        except:
            return 1.0

    def getSigmoidEq(self, x1, y1, x2, y2):
        slope = (self.invY(y2) - self.invY(y1)) / (x2 - x1)
        intercept = self.invY(y1) - slope * x1
        self.cef = [slope, intercept]
        # print("CEF:", self.cef)

    def getEqString(self):
        val1 = self.cef[1]
        return "1/(1+e^(" + self.cefString(self.cef[0], 1, showPlus=False) + self.cefString(self.cef[1], 0) + "))"


class SVM(SVMBase):
    def __init__(self, C=0.005, n_iters=10000, learning_rate=0.000001, **kwargs):
        super().__init__(**kwargs)
        # Length is 3: 2 to define the line and the width
        self.c = C
        self.iter = n_iters
        self.eta = learning_rate
        self.reset()  # no reset in classifer init90
        # print("X Shape:", self.table.x.shape)
        # print("W Shape:", self.w.shape)

    def setTable(self, **kwargs):
        super().setTable(**kwargs)
        self.data = {-1: [], 1: []}
        for i in range(self.table.rowCount):
            self.data[self.table.y[i][0]].append(self.table.x[i])
        self.opt_dict = {}
        self.transforms = [[1, 1], [-1, 1], [-1, -1], [1, -1]]

        self.all_data = np.array([])
        for yi in self.data:
            self.all_data = np.append(self.all_data, self.data[yi])
        self.max_feature_value = max(self.all_data)
        self.min_feature_value = min(self.all_data)
        self.all_data = None

        # with smaller steps our margins and db will be more precise
        self.step_sizes = [self.max_feature_value * 0.1,
                           self.max_feature_value * 0.01,
                           # point of expense
                           self.max_feature_value * 0.001, ]

        # extremly expensise
        self.b_range_multiple = 5
        # we dont need to take as small step as w
        self.b_multiple = 5

        self.latest_optimum = self.max_feature_value * 10
        self.stepIndex = 0

    def reset(self):
        super().reset()
        self.costs = np.zeros(self.iter)
        self.counter = 0
        self.reg_strength = 10000

    def fit(self):
        if self.stepIndex >= len(self.step_sizes):
            self.isRunning = False
            print("Training Done")
            return
        step = self.step_sizes[self.stepIndex]
        self.stepIndex += 1

        w = np.array([self.latest_optimum, self.latest_optimum])

        # we can do this because convex
        optimized = False
        while not optimized:
            for b in np.arange(-1 * self.max_feature_value * self.b_range_multiple,
                               self.max_feature_value * self.b_range_multiple,
                               step * self.b_multiple):
                for transformation in self.transforms:
                    w_t = w * transformation
                    found_option = True

                    # weakest link in SVM fundamentally
                    # SMO attempts to fix this a bit
                    # ti(xi.w+b) >=1
                    for i in self.data:
                        for xi in self.data[i]:
                            yi = i
                            if not yi * (np.dot(w_t, xi) + b) >= 1:
                                found_option = False
                                break
                    if found_option:
                        """
                        all points in dataset satisfy y(w.x)+b>=1 for this cuurent w_t, b
                        then put w,b in dict with ||w|| as key
                        """
                        self.opt_dict[np.linalg.norm(w_t)] = [w_t, b]

            # after w[0] or w[1]<0 then values of w starts repeating itself because of transformation
            # Think about it, it is easy
            # print(w,len(self.opt_dict)) Try printing to understand
            if w[0] < 0:
                optimized = True
                # print("optimized a step")
            else:
                w = w - step

        # sorting ||w|| to put the smallest ||w|| at poition 0
        norms = sorted([n for n in self.opt_dict])
        # optimal values of w,b
        opt_choice = self.opt_dict[norms[0]]

        self.w = opt_choice[0]
        self.b = opt_choice[1]

        # start with new self.latest_optimum (initial values for w)
        self.latest_optimum = opt_choice[0][0] + step * 2
        self.updateGraphics()

    def getPts(self, start=None, end=None, count=40):  # get many points
        return [self.getLinearPts(
            isLinear=True,
            stripeCount=False if v == 0 else 30,
            m=-self.w[0] / self.w[1],
            b=(v - self.b) / self.w[1],
            v=v
        ) for v in [0, -1, 1]]
    # def getPts(self, start=None, end=None, count=40):  # get many points
    #     return [self.getLinearPts(isLinear=True, v=v) for v in [0, -1, 1]]

    def predict(self, x):
        return 1 if (x @ self.w.T + self.b) >= 0 else -1
        # return [1 if i >= 0 else 0 for i in (x @ self.w.T + self.b)]

    def getEq(self):
        x1, y1 = self.critPts[0] if len(self.critPts) > 1 else (0, 0)
        x2, y2 = self.critPts[1] if len(self.critPts) > 1 else (x1 + 1, y1)
        x3, y3 = self.critPts[2] if len(self.critPts) > 2 else (x1, y1 - 1)
        try:
            res = hp.solveEquations(a=np.array([[y1, x1, 1], [y2, x2, 1], [y3, x3, 1]]), b=np.array([0, 0, 1]))
            self.w = np.array([res[1], res[0]])
            self.b = res[2]
        except:
            pass


if __name__ == '__main__':
    hp.clear()
    print("Running Models MAIN")
    # from table import Table
    # table = Table(filePath="examples/decisionTree/small").createXXYTable()
    # train, test = table.partition()
    # knn = KNN(table=train, partition=0.8, k=3)
    # print("Accuracy:", 100 * knn.accuracy(testTable=test))
    # for _x in knn.x:
    #     print(_x, end=" Closest: ")
    #     for j in knn.getNeighbor(_x):
    #         print(knn.x[j], knn.y[j], end=" | ")
    #     print()
