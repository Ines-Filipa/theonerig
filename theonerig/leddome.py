# AUTOGENERATED! DO NOT EDIT! File to edit: 13_leddome.ipynb (unless otherwise specified).

__all__ = ['get_dome_positions', 'as_cartesian', 'as_spherical']

# Cell
import numpy as np
import math

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Cell
def get_dome_positions(mode="cartesian"):
    """
    Generates positions of all LEDs of the dome. Position of first and last LED of each stripe
    were estimated in Blender, and other in between LEDs position are interpolated from those two.

    params:
        - mode: What coordinates to obtain in set ["cartesian", "spherical"]
    return:
        - LED position of the LED dome, in shape (4, 237)
    """
    stripe_dict = {}
    stripe = np.array([[-0.44162,0.46045,10.07932], [-0.03378,10.07122,0.72211]])*10
    stripe_dict["A"] = _slerp(stripe, 23)

    stripe = np.array([[0.42254,1.33094,10.00507], [0.83062,9.99418,1.12168]])*10
    stripe_dict["B"] = _slerp(stripe, 21)

    stripe = np.array([[-1.3044,1.33575,9.94323], [-0.93444, 10.00996,0.99274]])*10
    stripe_dict["C"] = _slerp(stripe, 21)

    stripe = np.array([[1.35075,2.2321,9.75535], [1.68846,9.91944,0.77928]])*10
    stripe_dict["D"] = _slerp(stripe, 20)

    stripe = np.array([[-2.20708,2.29345,9.58381], [-1.8337,9.92046,1.14081]])*10
    stripe_dict["E"] = _slerp(stripe, 19)

    stripe = np.array([[2.31814,3.13993,9.31365], [2.52401,9.74959,0.86306]])*10
    stripe_dict["F"] = _slerp(stripe, 18)

    stripe = np.array([[-3.15667,3.31007,9.00523], [-2.69219,9.68376,1.0918]])*10
    stripe_dict["G"] = _slerp(stripe, 17)

    stripe = np.array([[3.3186,4.12493,8.60008], [3.28828,9.52856,0.61278]])*10
    stripe_dict["H"] = _slerp(stripe, 16)

    stripe = np.array([[-4.0779,4.27888,8.18478], [-3.45295,9.45243,0.77226]])*10
    stripe_dict["I"] = _slerp(stripe, 15)

    stripe = np.array([[4.29328,5.00709,7.63564], [4.17924,9.14635,1.03659]])*10
    stripe_dict["J"] = _slerp(stripe, 13)

    stripe = np.array([[-4.99026,5.24451,7.06361], [-4.3501,9.07599,1.00064]])*10
    stripe_dict["K"] = _slerp(stripe, 12)

    stripe = np.array([[5.22638,5.86208,6.3335], [4.85207,8.84847,0.57339]])*10
    stripe_dict["L"] = _slerp(stripe, 11)

    stripe = np.array([[-5.77797,6.10141,5.60405], [-5.14097,8.63676,1.02421]])*10
    stripe_dict["M"] = _slerp(stripe, 9)

    stripe = np.array([[6.03059,6.57628,4.71668], [5.55174,8.42348,0.46679]])*10
    stripe_dict["N"] = _slerp(stripe, 8)

    stripe = np.array([[-6.40277,6.82204,3.80993], [-5.84937,8.19519,0.84915]])*10
    stripe_dict["O"] = _slerp(stripe, 6)

    stripe = np.array([[6.62294,7.08816,2.77088], [6.34649,7.81552,0.85683]])*10
    stripe_dict["P"] = _slerp(stripe, 4)

    stripe = np.array([[-6.77734,7.27747,1.7878], [-6.49463,7.71771,0.6162]])*10
    stripe_dict["Q"] = _slerp(stripe, 3)

    stripe = np.array([[6.94329,7.30411,0.65871]])*10
    stripe_dict["R"] = stripe

    res = _symetry_stripes(_chain_stripes(stripe_dict))
    if mode=="spherical":
        res = np.apply_along_axis(as_spherical, axis=-1, arr=res)
    return res

def _symetry_stripes(stripe):
    """
    Generates the 90° symetry of three stripes from the given stripe.
    """
    all_stripes = np.stack([stripe]*4, axis=0)
    tmp = all_stripes[1,:,0]*-1
    all_stripes[1,:,0] = all_stripes[1,:,1]
    all_stripes[1,:,1] = tmp

    all_stripes[2,:,0] *= -1
    all_stripes[2,:,1] *= -1

    tmp = all_stripes[3,:,1]*-1
    all_stripes[3,:,1] = all_stripes[3,:,0]
    all_stripes[3,:,0] = tmp
    return all_stripes

def _slerp(leds_xyz, n_led):
    """Interpolate positions from the xyz positon of the first and last LED

    params:
        -leds_xyz: np.array of shape(2,3)
        -n_led: total n LED on the stripe
    return:
        - interpolated positions
    """
    p0, p1 = leds_xyz[0], leds_xyz[1]

    omega = math.acos(np.dot(p0/np.linalg.norm(p0), p1/np.linalg.norm(p1)))
    so = math.sin(omega)
    return [math.sin((1.0-t)*omega) / so * p0 + math.sin(t*omega)/so * p1 for t in np.linspace(0.0, 1.0, n_led)]

def as_cartesian(rthetaphi):
    """
    Convert 3D polar coordinate tuple into cartesian coordinates.

    params:
        - rthetaphi: Single or list of (r, theta, phi) iterable
    return:
        - Single or list of converted (x, y, z) array.
    """
    r, theta, phi = tuple(np.array(rthetaphi).T)
    theta   = theta*np.pi/180 # to radian
    phi     = phi*np.pi/180
    x = r * np.sin( theta ) * np.cos( phi )
    y = r * np.sin( theta ) * np.sin( phi )
    z = r * np.cos( theta )
    return np.stack([x,y,z], axis=-1)

def as_spherical(xyz):
    """
    Convert 3D cartesian coordinates tuple into polar coordinate.

    params:
        - xyz: Single or list of (x, y, z) iterable
    return:
        - Single or list of converted (r, theta, phi) array.
    """
    x, y, z = tuple(np.array(xyz).T)
    r       =  np.sqrt(x*x + y*y + z*z)
    theta   =  np.arccos(z/r)
    phi     =  np.arctan2(y,x)
    return np.stack([r,theta,phi], axis=-1)

def _chain_stripes(stripe_dict):
    """
    Chain the stripes to create a one-dimensional array were LED idx correspond to their index on the stripe,
    with left side first.
    """
    res = []
    UP,DOWN = -1,1
    ori = UP
    left_side = ["B","D","F","H","J","L","N","P","R"]
    for key in left_side:
        res.extend(stripe_dict[key][::ori])
        ori *= -1

    ori = UP
    right_side = ["Q","O","M","K","I","G","E","C","A"]
    for key in right_side:
        res.extend(stripe_dict[key][::ori])
        ori *= -1
    return np.array(res)