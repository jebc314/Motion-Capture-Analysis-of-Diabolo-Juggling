import vectormath as vmath
import pandas as pd
from diabolo_motion_classes import *

# Use the data from circular_accel_stick_motion.csv
# and the parameters for that file for testing
# Stick right
# Rotation: wxyz, Position: xyz
# -0.568394 0.220991	-0.107013	-0.785264	0.169167	0.012684	0.892141
stick_right_inital_orientation = MyQuaternion(-0.568394, 0.220991, -0.107013, -0.785264)
stick_right_inital_position = vmath.Vector3(0.169167, 0.012684, 0.892141)
stick_right_pose = Pose(stick_right_inital_position, stick_right_inital_orientation)
# Diabolo
# 0.068687	-0.635083	-0.76354	0.094653	0.245212	0.116809	0.451904
diabolo_inital_orientation = MyQuaternion(0.068687, -0.635083, -0.76354, 0.094653)
diabolo_inital_position = vmath.Vector3(0.245212, 0.116809, 0.451904)
diabolo_pose = Pose(diabolo_inital_position, diabolo_inital_orientation)
# Stick left
# 0.21318	0.407518	0.709749	0.53361	-0.536085	-0.127391	1.104165
stick_left_inital_orientation = MyQuaternion(0.21318, 0.407518, 0.709749, 0.53361)
stick_left_inital_position = vmath.Vector3(-0.536085, -0.127391, 1.104165)
stick_left_pose = Pose(stick_left_inital_position, stick_left_inital_orientation)

# initial_poses: PoseArray: diabolo, left, right
initial_poses = PoseArray([diabolo_pose, stick_left_pose, stick_right_pose])

rot_velocity = 25 # seems arbitary

trans_velocity = vmath.Vector3(0,0,0) # it looks like this is the default

# pull velocity scale
pv_pre_cap_scale = 0.13
pv_post_cap_scale = 0.13	
pv_cap_scale = 0.07

velocity_diffusion_factor = 0.9999
time_step = 5/600
caps_valid = False
mass = 0.2 # kg
axle_radius = 0.0065
string_length = 1.58 # meters
file_name = "data.csv"

initial_state = DiaboloSimConfig(
    initial_poses,
    rot_velocity,
    trans_velocity, 
    pv_pre_cap_scale, 
    pv_cap_scale,
    pv_post_cap_scale,
    velocity_diffusion_factor,
    time_step,
    caps_valid,
    mass,
    axle_radius,
    string_length,
    file_name
)

print(initial_state)

def generate_stick_poses_from_file(csv_file):
    df = pd.read_csv(csv_file)
    stick_right_poses = PoseArray([])
    stick_left_poses = PoseArray([])
    times = []
    for i in range(len(df)):
        row = df.iloc[i]
        stick_right_pose = Pose(
            vmath.Vector3(
                row['stick_right-positionX'],
                row['stick_right-positionY'],
                row['stick_right-positionZ']
            ), MyQuaternion(
                x = row['stick_right-rotationX'],
                y = row['stick_right-rotationY'],
                z = row['stick_right-rotationZ'],
                w = row['stick_right-rotationW']
            ))
        stick_left_pose = Pose(
            vmath.Vector3(
                row['stick_left-positionX'],
                row['stick_left-positionY'],
                row['stick_left-positionZ']
            ), MyQuaternion(
                x = row['stick_left-rotationX'],
                y = row['stick_left-rotationY'],
                z = row['stick_left-rotationZ'],
                w = row['stick_left-rotationW']
            ))
        stick_right_poses.poses.append(stick_right_pose)
        stick_left_poses.poses.append(stick_left_pose)
        times.append(row['Time (Seconds)'])
    return stick_left_poses, stick_right_poses, times

stick_left_poses, stick_right_poses, times = generate_stick_poses_from_file(
    'circular_accel_stick_motion_stick_poses.csv')

steps = len(stick_left_poses.poses)
planned_left_times = []
planned_right_times = []
for i in range(1, steps + 1):
    planned_left_times.append(i * time_step)
    planned_right_times.append(i * time_step)

dp = DiaboloPredictor(initial_state)
print(dp.initial_state_.initial_poses.poses[0])
predicted_states = []
# dp.constrain_to_2D_flag = True
dp.predict(stick_left_poses, stick_right_poses, planned_left_times, planned_right_times, predicted_states, True)

with open('output.csv', 'w') as f:
    for i in range(len(predicted_states)):
        position = predicted_states[i].pose.position
        f.write(f"{position.x},{position.y},{position.z}\n")