
from __future__ import division

import numpy as np


def step(t, xnow, xend, direction, old_beta, vmax, base):
    """ POSQ single step """
    k_v = 3.8
    k_rho = 1    # Condition: k_alpha + 5/3*k_beta - 2/pi*k_rho > 0 !
    k_alpha = 6
    k_beta = -1
    rho_end = 0.00510      # [m]

    if t == 0:
        old_beta = 0

    # extract coordinates
    xc, yc, tc = xnow[0], xnow[1], xnow[2]
    xe, ye, te = xend[0], xend[1], xend[2]

    # rho
    dx = xe - xc
    dy = ye - yc
    rho = np.sqrt(dx**2 + dy**2)
    f_rho = rho
    if f_rho > (vmax / k_rho):
        f_rho = vmax / k_rho

    # alpha
    alpha = normangle(np.arctan2(dy, dx) - tc, -np.pi)

    # direction (forward or backward)
    if direction == 1:
        if alpha > np.pi / 2:
            f_rho = -f_rho                   # backwards
            alpha = alpha - np.pi
        elif alpha <= -np.pi / 2:
            f_rho = -f_rho                   # backwards
            alpha = alpha + np.pi
    elif direction == -1:                  # arrive backwards
        f_rho = -f_rho
        alpha = alpha + np.pi
        if alpha > np.pi:
            alpha = alpha - 2 * np.pi

    # phi, beta
    phi = te - tc
    phi = normangle(phi, -np.pi)
    beta = normangle(phi - alpha, -np.pi)
    if abs(old_beta - beta) > np.pi:           # avoid instability
        beta = old_beta
    old_beta = beta

    vm = k_rho * np.tanh(f_rho * k_v)
    vd = (k_alpha * alpha + k_beta * beta)
    eot = (rho < rho_end)

    # Convert speed to wheel speeds
    vl = vm - vd * base / 2
    if abs(vl) > vmax:
        vl = vmax * np.sign(vl)

    vr = vm + vd * base / 2
    if abs(vr) > vmax:
        vr = vmax * np.sign(vr)

    return vl, vr, eot, vm, vd, old_beta


def normangle(theta, start=0):
    """ Normalize an angle to be in the range :math:`[0, 2\pi]`

    Parameters
    -----------
    theta : float
        input angle to normalize

    start: float
        input start angle (optional, default: 0.0)

    Returns
    --------
    res : float
        normalized angle or :math:`\infty`

    """
    if theta < np.inf:
        while theta >= start + 2 * np.pi:
            theta -= 2 * np.pi
        while theta < start:
            theta += 2 * np.pi
        return theta
    else:
        return np.inf
