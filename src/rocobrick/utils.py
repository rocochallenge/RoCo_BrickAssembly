import numpy as np
import math, json, time, os, sys, shutil
from copy import deepcopy
from scipy.spatial.transform import Rotation as R

"""
Utility functions for RoCo-BrickAssembly, including JSON handling, transformation utilities, and robot kinematics helpers.
"""

def load_json(fname):
    with open(fname, 'r') as file:
        data = json.load(file)
    file.close()
    return data

def rot_x(theta):
    return np.array([[1, 0, 0, 0],
                     [0, np.cos(theta), -np.sin(theta), 0],
                     [0, np.sin(theta), np.cos(theta), 0],
                     [0, 0, 0, 1]])

def rot_y(theta):
    return np.array([[np.cos(theta), 0, np.sin(theta), 0],
                     [0, 1, 0, 0],
                     [-np.sin(theta), 0, np.cos(theta), 0],
                     [0, 0, 0, 1]])

def rot_z(theta):
    return np.array([[np.cos(theta), -np.sin(theta), 0, 0],
                     [np.sin(theta), np.cos(theta), 0, 0],
                     [0, 0, 1, 0],
                     [0, 0, 0, 1]])

def trans_x(val): # (m)
    return np.array([[1, 0, 0, val],
                     [0, 1, 0, 0],
                     [0, 0, 1, 0],
                     [0, 0, 0, 1]])

def trans_y(val): # (m)
    return np.array([[1, 0, 0, 0],
                     [0, 1, 0, val],
                     [0, 0, 1, 0],
                     [0, 0, 0, 1]])

def trans_z(val): # (m)
    return np.array([[1, 0, 0, 0],
                     [0, 1, 0, 0],
                     [0, 0, 1, val],
                     [0, 0, 0, 1]])

def robot_T_to_world_T(robot_T, world_to_robot_T):
    return world_to_robot_T @ robot_T

def world_T_to_robot_T(world_T, world_to_robot_T):
    return np.linalg.inv(world_to_robot_T) @ world_T


def step_towards_transform(cur_T,
                           goal_T,
                           max_translation_step=0.005,   # meters
                           max_rotation_step_deg=0.005, # rad
                           ):
    """
    Move from cur_T toward goal_T with bounded linear/angular step.

    Args:
        cur_T:  4x4 current transform
        goal_T: 4x4 target transform

    Returns:
        next_T: stepped transform
    """

    next_T = np.eye(4)

    # =========================================================
    # Translation
    # =========================================================
    cur_t = cur_T[:3, 3]
    goal_t = goal_T[:3, 3]

    delta_t = goal_t - cur_t
    dist = np.linalg.norm(delta_t)

    if dist <= max_translation_step or dist < 1e-9:
        new_t = goal_t
    else:
        direction = delta_t / dist
        new_t = cur_t + direction * max_translation_step

    # =========================================================
    # Rotation
    # =========================================================
    cur_R = R.from_matrix(cur_T[:3, :3])
    goal_R = R.from_matrix(goal_T[:3, :3])

    # relative rotation
    rel_R = goal_R * cur_R.inv()

    rotvec = rel_R.as_rotvec()

    angle = np.linalg.norm(rotvec)

    max_angle = max_rotation_step_deg

    if angle <= max_angle or angle < 1e-9:
        new_R = goal_R

    else:
        axis = rotvec / angle

        clipped_rotvec = axis * max_angle

        step_R = R.from_rotvec(clipped_rotvec)

        new_R = step_R * cur_R

    # =========================================================
    # Assemble transform
    # =========================================================
    next_T[:3, :3] = new_R.as_matrix()
    next_T[:3, 3] = new_t

    return next_T


def deep_merge(a, b):
    result = a.copy()
    for k, v in b.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = deep_merge(result[k], v)
        else:
            result[k] = v
    return result

def to_jsonable(value):
    """Convert numpy values used in episode metadata into JSON-safe Python values."""
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, tuple):
        return [to_jsonable(v) for v in value]
    if isinstance(value, list):
        return [to_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {str(k): to_jsonable(v) for k, v in value.items()}
    return value
