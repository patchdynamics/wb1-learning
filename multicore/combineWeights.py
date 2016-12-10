import numpy as np
import sys, getopt

WEIGHTS_FILE = "weights.npy"
QVALUES_FILE = "qvalues.npy"
KNN_FILE = "knn.npy"

try:
    opts, args = getopt.getopt(sys.argv[1:],"t:n:a:")
except getopt.GetoptError:
    print 'combineWeights.py -t <tag> -n <number> -a <algorithm>'
    sys.exit()

for opt, arg in opts:
    if opt == '-t':
        dirTag = arg
    elif opt == '-n':
        numCores = int(arg)
    elif opt == '-a':
        algorithm = arg

if algorithm == "Linear":
    weights1 = np.load(dirTag + "1/" + WEIGHTS_FILE)
    weights = np.empty((numCores, weights1.shape[1], weights1.shape[2]))
    for i in range(numCores):
        weights[i] = np.load(dirTag + str(i+1) + "/" + WEIGHTS_FILE)
    maskedMeanWeights = np.ma.masked_equal(weights, 0).mean(axis=0)
    meanWeights = np.ma.filled(maskedMeanWeights, 0)
    meanWeights = np.expand_dims(meanWeights, axis=0)
    for i in range(numCores + 1):
        np.save(dirTag + str(i) + "/" + WEIGHTS_FILE, meanWeights)

else:
    if algorithm == "Lookup":
        filename = QVALUES_FILE
    elif algorithm == "KNN":
        filename = KNN_FILE
    else:
        print "Unknown algorithm"
        sys.exit()

    keys = set()
    qvalues = []
    combined = {}
    for i in range(numCores):
        qvalues.append(np.load(dirTag + str(i+1) + "/" + filename)[0])
        keys.update(qvalues[i].keys())
    for key in keys:
        values = []
        for i in range(numCores):
            if key in qvalues[i]:
                values.append(qvalues[i][key])
        combined[key] = sum(values) / len(values)

    combinedArray = []
    combinedArray.append(combined)

    for i in range(numCores + 1):
        np.save(dirTag + str(i) + "/" + filename, combinedArray)
