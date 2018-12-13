import itertools
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from readRunFile import loadRex


def label(controlLabel):
    listLabel = []
    for lab in controlLabel:
        listLabel.append(float(lab.split("%")[0]))
    return listLabel


def polyfit2d(x, y, z, orderx=2, ordery=3):
    ncols = (orderx + 1) * (ordery + 1)
    G = np.zeros((x.size, ncols))
    ij = itertools.product(range(orderx + 1), range(ordery + 1))
    for k, (i, j) in enumerate(ij):
        G[:, k] = x ** i * y ** j
    m, _, _, _ = np.linalg.lstsq(G, z)
    return m


def polyval2d(x, y, m, orderx=2, ordery=3):
    # order = int(np.sqrt(len(m))) - 1
    ij = itertools.product(range(orderx + 1), range(ordery + 1))
    z = np.zeros_like(x)
    for a, (i, j) in zip(m, ij):
        z += a * x ** i * y ** j
    return z


if __name__ == "__main__":

    FNameREXList = "RexList.txt"
    with open(FNameREXList) as fp:
        listREXNames = fp.read().splitlines()

    REXName = listREXNames[10]
    FNameREX = "./RexFiles/" + REXName

    # read the rex file to get the data.
    try:
        control, controlQpcr, exp, expQpcr, controlLabel, expLabel, numControl, numExp, temperature = loadRex(
            FNameREX
        )
    except:
        print("error reading", FNameREX)
        raise

    labelControl = label(controlLabel[2:])

    """
    fig = plt.figure()
    plt.plot(control[2:].T)
    plt.legend(labels=controlLabel[2:])
    plt.show(block=False)
    """

    # x axis is percentage meth
    x = np.repeat(np.array(labelControl), control.shape[1])
    # y axis is temperate
    y = np.array(list(range(control.shape[1])) * len(labelControl))
    z = np.squeeze(control[2:].reshape(1, -1))

    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(x, y, z)
    plt.show(block=False)
    """

    orderx, ordery = 2, 5
    # Fit a 3rd order, 2d polynomial
    m = polyfit2d(x, y, z, orderx=orderx, ordery=ordery)

    # Evaluate it on a grid...
    nx, ny = 10, 30
    # nx, ny = 101, len(y)
    xx, yy = np.meshgrid(np.linspace(0, 100, nx), np.linspace(y.min(), y.max(), ny))
    zz = polyval2d(xx, yy, m, orderx=orderx, ordery=ordery)

    # Plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(xx, yy, zz)
    ax.scatter(x, y, z, c="r")
    plt.show(block=False)

    """
    # Generate Data...
    numdata = 100
    x = np.random.random(numdata)
    y = np.random.random(numdata)
    z = x ** 2 + y ** 2 + 3 * x ** 3 + y + np.random.random(numdata)

    # Fit a 3rd order, 2d polynomial
    m = polyfit2d(x, y, z)

    # Evaluate it on a grid...
    nx, ny = 20, 20
    xx, yy = np.meshgrid(
        np.linspace(x.min(), x.max(), nx), np.linspace(y.min(), y.max(), ny)
    )
    zz = polyval2d(xx, yy, m)

    # Plot
    plt.imshow(zz, extent=(x.min(), y.max(), x.max(), y.min()))
    plt.scatter(x, y, c=z)
    plt.show()
    """


def filter_signal(control):

    fig = plt.figure()
    plt.plot(abs(np.fft.rfft(control[2:, :], 512, axis=1)).T)
    plt.show()

    # make a LP filter that has a 3db cutoff where the bulk of the signal ends.
    # return a the control signal after applying that filter.

    return 1
