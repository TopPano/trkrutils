import numpy as np
import math

def estimate_eao_interval(sequence_lengths, threshold):
    model = _gmm_estimate(sequence_lengths)

    # Tabulate the GMM from zero to max length
    x = range(1, max(sequence_lengths) + 1)
    p = _gmm_evaluate(model, x)
    p = np.divide(p, sum(p)).tolist()

    low, high = _find_range(p, threshold)
    peak = np.argmax(p) + 1

    return peak,low,high

# _gmm_estimate Estimates a GMM on a set of points
#
# Originally a part of: Maggot (developed within EU project CogX)
# Original author: Matej Kristan, 2009
#
# Input:
# data (matrix): Points for which to estimate a model
#
# Output:
# model (vector): values for corresponding points
def _gmm_estimate(data):
    N = len(data)
    model = dict()
    model['Mu'] = list(data)
    model['Cov'] = np.zeros(N).tolist()
    model['w'] = np.full(N, 1. / N).tolist()

    pdf0 = dict(model)

    # First we'll spherize the distribution
    Mu, C = _spherize(pdf0['Mu'], pdf0['Cov'], pdf0['w'])
    U, S, V = np.linalg.svd([[C]])
    T = np.dot(np.diag(np.divide(1.0, np.sqrt(np.diag(S)))), U)[0]

    pdf0['Mu'] = np.subtract(pdf0['Mu'], Mu)
    pdf0['Mu'] = np.dot(T, pdf0['Mu']).tolist()
    pdf0['Cov'] = [np.dot(T, np.dot(cov, T)) for cov in pdf0['Cov']]

    C = np.dot(np.dot(T,C), T)
    H = _optimal_bandwidth(pdf0['Mu'], pdf0['Cov'], pdf0['w'], C, len(pdf0['w']))

    pdf = dict()
    pdf['Mu'] = Mu
    pdf['Cov'] = [H]
    pdf['w']= 1.0

    iT = np.linalg.inv([[T]])[0][0]
    pdf['Mu'] = iT * pdf['Mu']
    pdf['Mu'] = pdf['Mu'] + Mu
    pdf['Cov'][0] = iT * pdf['Cov'][0] * iT

    H = pdf['Cov'][0]
    model['Cov'] = np.full(N, H).tolist()

    return model

def _spherize(Mu, Cov, w):
    if len(w) == 1:
        new_mu = Mu[0]
        if len(Cov) > 0:
            new_Cov = Cov[0]
        else:
            new_Cov = 0.0
        return new_mu, new_Cov

    sumw = sum(w)
    _w = [(x / sumw) for x in w]
    new_mu = sum(np.multiply(Mu, _w))

    if len(Cov) > 0:
        new_Cov = sum(np.multiply(_w, np.add(Cov, np.multiply(Mu, Mu))))
    else:
        new_Cov = sum(np.multiply(_w, np.multiply(Mu, Mu)))
    new_Cov = new_Cov - new_mu * new_mu

    return new_mu, new_Cov

def _optimal_bandwidth(Mu, Cov, w, Cov_smp, N_eff):
    d = 1
    G = Cov_smp * math.pow((4.0 / ((d + 2) * N_eff)), (2.0 / (d + 4)))

    alpha_scale = 1
    # For numerical stability. it could have been: F = Cov_smp
    # could also constrain to say that F = identity!
    F = Cov_smp * alpha_scale
    Rf2 = _integral_squared_hessian(Mu, w, Cov, F, G)

    h_amise = math.pow(math.pow(N_eff, (-1)) * math.pow(np.linalg.det([[F]]), (-0.5)) / (math.pow(math.sqrt(4 * math.pi), d) * Rf2 * d), 1.0 / (d + 4))
    H = math.pow(F * h_amise, 2) * alpha_scale ;

    return H

# Calculates an integral over the squared Hessian of a Gaussian mixture model.
# Follows Wand and Jones "Kernel Smoothing", page 101., assuming H = h * F.
def _integral_squared_hessian(Mu, w, Cov, F, G):
    if not Mu:
        return float('nan')

    # Read dimension and number of components
    d = 1
    N = len(Mu)

    # Precompute normalizer constNorm = (1 / 2pi) ^ (d / 2)
    constNorm = math.pow((1.0 / (2 * math.pi)), (d / 2.0))
    I = 0

    # Test if F is identity for speedup
    delta_F = sum(sum(abs(np.subtract(F, np.identity(1)))))
    if delta_F < 0.001:
        # Generate a summation over the nonsymmetric matrix
        for l1 in range(N):
            S1 = Cov[l1] + G
            Mu1 = Mu[l1]
            w1 = w[l1]
            for l2 in range(l1, N):
                S2 = Cov[l2]
                Mu2 = Mu[l2]
                w2 = w[l2]
                A = np.linalg.inv([[S1 + S2]])
                dm = Mu1 - Mu2
                m = np.dot(np.dot(dm, A), dm)[0][0]
                f_t = constNorm * math.sqrt(np.linalg.det(A)) * math.exp(np.dot(-0.5, m))
                c = 2 * sum(sum(np.multiply(A, np.transpose(A)))) * (1 - 2 * m) + math.pow(1 - m, 2) * math.pow(np.trace(A), 2)

                # Determine the weight of the term current
                if l1 == l2:
                    eta = 1
                else:
                    eta = 2
                I = I + f_t * c * w2 * w1 * eta
    else:
        # Generate a summation over the nonsymmetric matrix
        for l1 in range(N):
            S1 = Cov[l1]
            Mu1 =Mu[l1]
            w1 = w[l1]
            for l2 in range(l1, N):
                S2 = Cov[l2] + G
                Mu2 = Mu[l2]
                w2 = w[l2]
                A = np.linalg.inv([[S1 + S2]])
                dm = Mu1 - Mu2
                ds = np.dot(dm, A)
                b = np.dot(ds, ds)
                B = np.subtract(A, np.multiply(2, b))
                C = np.subtract(A, b)

                f_t = constNorm * math.sqrt(np.linalg.det(A)) * math.exp(-0.5 * ds * dm)
                c = 2 * np.trace(F * A * F * B) + math.pow(np.trace(F * C), 2)

                # Determine the weight of the term current
                if l1 == l2:
                    eta = 1
                else:
                    eta = 2
                I = I + f_t * c * w2 * w1 * eta

    return I

# _gmm_evaluate Evaluates the GMM for a set of points
#
# Input:
# model (struct): A gaussian mixture model structure
# X (matrix): Points for which to evaluate the model
#
# Output:
# p (vector): values for corresponding points
def _gmm_evaluate(model, X):
    d = 1
    num_data = len(X)
    p = np.zeros(num_data)

    for idx in range(len(model['w'])):
        iS = np.linalg.cholesky(np.linalg.inv([[model['Cov'][idx]]]))
        logdetiS = sum(np.log(np.diag(iS)))
        # log2pi = 1.83787706640935
        logConstant = logdetiS - 0.5 * d * 1.83787706640935
        dx = np.subtract(X, np.full(num_data, model['Mu'][idx])).tolist()
        dx = np.multiply(iS[0][0], dx)
        pl = np.subtract(logConstant, np.multiply(0.5, np.multiply(dx, dx)))
        p_tmp = np.exp(pl)
        p = np.add(p, np.multiply(model['w'][idx], p_tmp)).tolist()

    return p

def _find_range(p, density):
    # Find maximum on the KDE
    x_max = np.argmax(p)
    low = x_max
    high = x_max

    for idx in range(len(p) + 1):
        x_lo_tmp = low - 1
        x_hi_tmp = high + 1

        # Boundary indicator
        sw_lo = 0
        sw_hi = 0
        # Clip
        if x_lo_tmp <= 0:
            x_lo_tmp = 1
            sw_lo = 1
        if x_hi_tmp >= len(p):
            x_hi_tmp = len(p)
            sw_hi = 1

        # Increase left or right boundary
        if sw_lo == 1 and sw_hi == 1:
            low = x_lo_tmp
            high = x_hi_tmp
            break
        elif sw_lo == 0 and sw_hi == 0:
            if p[x_lo_tmp] > p[x_hi_tmp]:
                low = x_lo_tmp
            else:
                high = x_hi_tmp
        else:
            if sw_lo == 0:
                low = x_lo_tmp
            else:
                high = x_hi_tmp

        # Check the integral under the range
        s_p = sum(p[low : high + 1])
        if s_p >= density:
            return low + 1, high + 1
