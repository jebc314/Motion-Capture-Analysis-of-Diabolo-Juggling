import os
from flask import Flask, render_template,request
from vicon_dssdk import ViconDataStream
from flask_socketio import SocketIO, emit

import time
import json

client = ViconDataStream.Client()
frames = []
print( 'Connecting' )

# Comment this out if not connected to Vicon Host PC
# start '''
while not client.IsConnected():
    print( '.' )
    client.Connect( '192.168.70.2:801' )
    time.sleep(1)
    print(client.GetFrame())
client.EnableSegmentData()
# end '''

UPLOAD_FOLDER = 'static/files'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
socketio = SocketIO(app)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/savedata", methods=["POST"])
def save():
    if request.method == 'POST':
        files = request.files.getlist('data')
        files[0].save(os.path.join(app.config['UPLOAD_FOLDER'], files[0].filename))
        return files[0].filename

import pandas as pd
from diabolo_motion_classes import *
from scipy.signal import savgol_filter
import tensorflow as tf
from tensorflow import keras
import json

@app.route("/predict", methods=["GET"])
def predict():
    data_location = request.args.get('data_location')
    df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], data_location))

    stick_right_inital_orientation = MyQuaternion()
    stick_right_inital_position = vmath.Vector3(
        df.iloc[0,:]['stick_right-TX'], 
        df.iloc[0,:]['stick_right-TY'], 
        df.iloc[0,:]['stick_right-TZ'])
    stick_right_pose = Pose(stick_right_inital_position, stick_right_inital_orientation)
    # Diabolo
    diabolo_inital_orientation = MyQuaternion()
    diabolo_inital_position = vmath.Vector3(
        df.iloc[0,:]['Diabolo-TX'], 
        df.iloc[0,:]['Diabolo-TY'], 
        df.iloc[0,:]['Diabolo-TZ'])
    diabolo_pose = Pose(diabolo_inital_position, diabolo_inital_orientation)
    # Stick left
    stick_left_inital_orientation = MyQuaternion()
    stick_left_inital_position = vmath.Vector3(
        df.iloc[0,:]['stick_left-TX'], 
        df.iloc[0,:]['stick_left-TY'], 
        df.iloc[0,:]['stick_left-TZ'])
    stick_left_pose = Pose(stick_left_inital_position, stick_left_inital_orientation)

    # initial_poses: PoseArray: diabolo, left, right
    initial_poses = PoseArray([diabolo_pose, stick_left_pose, stick_right_pose])

    rot_velocity = 58.010031855847146 # the approx starting value I got from my analysis

    trans_velocity = vmath.Vector3(0,0,0) # it looks like this is the default

    # pull velocity scale
    pv_pre_cap_scale = 0.13
    pv_post_cap_scale = 0.13	
    pv_cap_scale = 0.07

    velocity_diffusion_factor = 0.9999
    time_step = 1/600
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

    def generate_stick_poses_from_df(df):
        stick_right_poses = PoseArray([])
        stick_left_poses = PoseArray([])
        times = []
        for i in range(len(df)):
            row = df.iloc[i]
            stick_right_pose = Pose(
                vmath.Vector3(
                    row['stick_right-TX'],
                    row['stick_right-TY'],
                    row['stick_right-TZ']
                ), MyQuaternion())
            stick_left_pose = Pose(
                vmath.Vector3(
                    row['stick_left-TX'],
                    row['stick_left-TY'],
                    row['stick_left-TZ']
                ), MyQuaternion())
            stick_right_poses.poses.append(stick_right_pose)
            stick_left_poses.poses.append(stick_left_pose)
            times.append((i) * time_step)
        return stick_left_poses, stick_right_poses, times

    stick_left_poses, stick_right_poses, times = generate_stick_poses_from_df(df)

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

    print(predicted_states[-1].pose.position)

    with open('static/files/output.csv', 'w') as f:
        f.write("X,Y,Z,W\n")
        for i in range(len(predicted_states)):
            position = predicted_states[i].pose.position
            rotational_velocity = predicted_states[i].rot_velocity
            f.write(f"{position.x},{position.y},{position.z},{rotational_velocity}\n")

    df_output = pd.read_csv('static/files/output.csv')

    pitch_angles = []
    offset_angles = []
    for i in range(len(df)):
        line = df.iloc[i]
        q = MyQuaternion(
            x=line['Diabolo-RX'],
            y=line['Diabolo-RY'],
            z=line['Diabolo-RZ'],
            w=line['Diabolo-RW'])

        direction_vector = vmath.Vector3(q.rotate([0,0,1]))
        horizontal_vector = vmath.Vector3(direction_vector[0], direction_vector[1], 0)
        horizontal_vector = horizontal_vector.normalize()

        if i == 0:
            pitch_angle = math.acos(direction_vector.dot(horizontal_vector))
            if (direction_vector[2]<=0):
                pitch_angle *= -1
            pitch_angles.append(pitch_angle)

        stick_right_vector = vmath.Vector3(
            line['stick_right-TX'],
            line['stick_right-TY'],
            line['stick_right-TZ']
        )
        stick_left_vector = vmath.Vector3(
            line['stick_left-TX'],
            line['stick_left-TY'],
            line['stick_left-TZ']
        )

        stick_diff_vector = stick_right_vector - stick_left_vector
        stick_diff_vector = vmath.Vector3(stick_diff_vector[0], stick_diff_vector[1], 0)
        stick_diff_vector = stick_diff_vector.normalize()

        offset_angle = math.pi/2 - math.acos(stick_diff_vector.dot(horizontal_vector))
        offset_angles.append(-offset_angle)
    
    smoothed_offset_angles = savgol_filter(offset_angles, 101, 5)
    x = smoothed_offset_angles
    xi = np.arange(len(x))
    mask = np.isfinite(x)
    xfiltered_offset = np.interp(xi, xi[mask], x[mask])

    offset_angularspeed = []

    for i in range(len(df)):
        time_index = i
        offset_angularspeed.append(xfiltered_offset[time_index]/(df_output.iloc[i]['W']))

    predicted_change_in_pitch = []
    predicted_pitch = [pitch_angles[0]]

    for i in range(len(df)):
        ratio_offset_speed = xfiltered_offset[i]/(df_output.iloc[i]['W'])
        change_in_pitch_value = ratio_offset_speed * 0.0018583839918719272
        predicted_change_in_pitch.append(change_in_pitch_value)
        predicted_pitch.append(predicted_pitch[-1] + change_in_pitch_value)

    test_values = []

    for i in range(len(df)-1):
        line_original = df.iloc[i]
        
        # positions
        x_diabolo = vmath.Vector3(
            line_original['Diabolo-TX'],
            line_original['Diabolo-TY'],
            line_original['Diabolo-TZ'])
        x_left = vmath.Vector3(
            line_original['stick_left-TX'],
            line_original['stick_left-TY'],
            line_original['stick_left-TZ'])
        x_right = vmath.Vector3(
            line_original['stick_right-TX'],
            line_original['stick_right-TY'],
            line_original['stick_right-TZ'])
        x_center = (x_left-x_right)/2
        x_diabolo_p = x_diabolo - x_center
        x_left_p = x_left - x_center
        x_right_p = x_right - x_center

        # velocity
        line_original_next = df.iloc[i+1]
        x_diabolo_next = vmath.Vector3(
            line_original_next['Diabolo-TX'],
            line_original_next['Diabolo-TY'],
            line_original_next['Diabolo-TZ'])

        v_diabolo = (x_diabolo_next - x_diabolo) * 600

        # next stick values
        x_left_next = vmath.Vector3(
            line_original_next['stick_left-TX'],
            line_original_next['stick_left-TY'],
            line_original_next['stick_left-TZ'])
        x_right_next = vmath.Vector3(
            line_original_next['stick_right-TX'],
            line_original_next['stick_right-TY'],
            line_original_next['stick_right-TZ'])
        x_center_next = (x_left_next-x_right_next)/2
        x_left_next_p = x_left_next - x_center_next
        x_right_next_p = x_right_next - x_center_next

        test_values.append([
            x_diabolo_p.x,
            x_diabolo_p.y,
            x_diabolo_p.z,
            v_diabolo.x,
            v_diabolo.y,
            v_diabolo.z,
            df_output.iloc[i]['W'],
            x_right_next_p.x,
            x_right_next_p.y,
            x_right_next_p.z,
            x_left_next_p.x,
            x_left_next_p.y,
            x_left_next_p.z,
            x_right_p.x,
            x_right_p.y,
            x_right_p.z,
            x_left_p.x,
            x_left_p.y,
            x_left_p.z
        ])

    test_values = np.array(test_values)

    df_test = pd.DataFrame(test_values, columns=[
    'x_diabolo_p.x',
    'x_diabolo_p.y',
    'x_diabolo_p.z',
    'v_diabolo.x',
    'v_diabolo.y',
    'v_diabolo.z',
    'w',
    'x_right_next_p.x',
    'x_right_next_p.y',
    'x_right_next_p.z',
    'x_left_next_p.x',
    'x_left_next_p.y',
    'x_left_next_p.z',
    'x_right_p.x',
    'x_right_p.y',
    'x_right_p.z',
    'x_left_p.x',
    'x_left_p.y',
    'x_left_p.z'
    ])

    model =  tf.keras.models.load_model('my_model_ll')

    prediction_output = model(test_values)

    print(len(test_values), len(prediction_output))

    stick_left_q = MyQuaternion(
        w=df.iloc[0]["stick_left-RW"],
        x=df.iloc[0]["stick_left-RX"],
        y=df.iloc[0]["stick_left-RY"],
        z=df.iloc[0]["stick_left-RZ"],
    )
    stick_left_euler = stick_left_q.toEuler()
    stick_right_q = MyQuaternion(
        w=df.iloc[0]["stick_right-RW"],
        x=df.iloc[0]["stick_right-RX"],
        y=df.iloc[0]["stick_right-RY"],
        z=df.iloc[0]["stick_right-RZ"],
    )
    stick_right_euler = stick_right_q.toEuler()

    output = [
        {
            "Diabolo-RX": np.pi / 2 + predicted_pitch[0],
            "Diabolo-RY": 0,
            "Diabolo-RZ": 0,
            "Diabolo-TX": (df_output.iloc[0]['X']) * 1000,
            "Diabolo-TY": (df_output.iloc[0]['Y']) * 1000,
            "Diabolo-TZ": (df_output.iloc[0]['Z']) * 1000,
            "stick_left-RX": stick_left_euler[0],
            "stick_left-RY": stick_left_euler[1],
            "stick_left-RZ": stick_left_euler[2],
            "stick_left-TX": df.iloc[0]["stick_left-TX"] * 1000,
            "stick_left-TY": df.iloc[0]["stick_left-TY"] * 1000,
            "stick_left-TZ": df.iloc[0]["stick_left-TZ"] * 1000,
            "stick_right-RX": stick_right_euler[0],
            "stick_right-RY": stick_right_euler[1],
            "stick_right-RZ": stick_right_euler[2],
            "stick_right-TX": df.iloc[0]["stick_right-TX"] * 1000,
            "stick_right-TY": df.iloc[0]["stick_right-TY"] * 1000,
            "stick_right-TZ": df.iloc[0]["stick_right-TZ"] * 1000
        }
    ]
    for i in range(len(df)-1):
        stick_left_q = MyQuaternion(
            w=df.iloc[i+1]["stick_left-RW"],
            x=df.iloc[i+1]["stick_left-RX"],
            y=df.iloc[i+1]["stick_left-RY"],
            z=df.iloc[i+1]["stick_left-RZ"],
        )
        stick_left_euler = stick_left_q.toEuler()
        stick_right_q = MyQuaternion(
            w=df.iloc[i+1]["stick_right-RW"],
            x=df.iloc[i+1]["stick_right-RX"],
            y=df.iloc[i+1]["stick_right-RY"],
            z=df.iloc[i+1]["stick_right-RZ"],
        )
        stick_right_euler = stick_right_q.toEuler()
        line = {
            "Diabolo-RX": np.pi / 2 + predicted_pitch[i+1] + prediction_output[i].numpy()[3],
            "Diabolo-RY": 0,
            "Diabolo-RZ": 0,
            "Diabolo-TX": (df_output.iloc[i+1]['X'] + prediction_output[i].numpy()[0]) * 1000,
            "Diabolo-TY": (df_output.iloc[i+1]['Y'] + prediction_output[i].numpy()[1]) * 1000,
            "Diabolo-TZ": (df_output.iloc[i+1]['Z'] + prediction_output[i].numpy()[2]) * 1000,
            "stick_left-RX":stick_left_euler[0],
            "stick_left-RY":stick_left_euler[1],
            "stick_left-RZ":stick_left_euler[2],
            "stick_left-TX": df.iloc[i+1]["stick_left-TX"] * 1000,
            "stick_left-TY": df.iloc[i+1]["stick_left-TY"] * 1000,
            "stick_left-TZ": df.iloc[i+1]["stick_left-TZ"] * 1000,
            "stick_right-RX": stick_right_euler[0],
            "stick_right-RY": stick_right_euler[1],
            "stick_right-RZ": stick_right_euler[2],
            "stick_right-TX": df.iloc[i+1]["stick_right-TX"] * 1000,
            "stick_right-TY": df.iloc[i+1]["stick_right-TY"] * 1000,
            "stick_right-TZ": df.iloc[i+1]["stick_right-TZ"] * 1000
        }

        output.append(line)

    json_output = json.dumps(output)

    with open('static/files/output.json', 'w') as f:
        f.write(json_output)

    return json_output

@socketio.on('getvicondata')
def after_connent():
    try:
        if client.GetFrame():
            #store data here
            frames.append(client.GetFrameNumber() )
        # Gets the objects in the scene
        subjectNames = client.GetSubjectNames()
        if True:
            objects_data = {}
            for subjectName in subjectNames:
                if subjectName not in ['Diabolo', 'stick_left', 'stick_right']:
                    continue
                print( subjectName )
                segmentNames = client.GetSegmentNames( subjectName )
                for segmentName in segmentNames:
                    segmentChildren = client.GetSegmentChildren( subjectName, segmentName )      
                    '''
                    emit_output = f"{segmentName} has global translation {client.GetSegmentGlobalTranslation( subjectName, segmentName )}\n\
                                    {segmentName} has global rotation( EulerXYZ ) {client.GetSegmentGlobalRotationEulerXYZ( subjectName, segmentName )}\n\
                                    {segmentName} has global rotation( Quaternion ) {client.GetSegmentGlobalRotationQuaternion( subjectName, segmentName )}"
                    emit('vicondata', emit_output)
                    '''
                    data = {
                        'GlobalTranslation':client.GetSegmentGlobalTranslation( subjectName, segmentName ),
                        'GlobalRotationEulerXYZ':client.GetSegmentGlobalRotationEulerXYZ( subjectName, segmentName ),
                        'GlobalRotationQuaternion':client.GetSegmentGlobalRotationQuaternion( subjectName, segmentName ),
                        'GlobalRotationHelical':client.GetSegmentGlobalRotationHelical( subjectName, segmentName ),
                        'GlobalRotationMatrix':client.GetSegmentGlobalRotationMatrix( subjectName, segmentName )
                    }
                    objects_data[subjectName] = data
                    #print( segmentName, 'has global translation', client.GetSegmentGlobalTranslation( subjectName, segmentName ) )
                    #print( segmentName, 'has global rotation( helical )', client.GetSegmentGlobalRotationHelical( subjectName, segmentName ) )               
                    #print( segmentName, 'has global rotation( EulerXYZ )', client.GetSegmentGlobalRotationEulerXYZ( subjectName, segmentName ) )               
                    #print( segmentName, 'has global rotation( Quaternion )', client.GetSegmentGlobalRotationQuaternion( subjectName, segmentName ) )               
                    #print( segmentName, 'has global rotation( Matrix )', client.GetSegmentGlobalRotationMatrix( subjectName, segmentName ) )
                    #print( segmentName, 'has local translation', client.GetSegmentLocalTranslation( subjectName, segmentName ) )
                    #print( segmentName, 'has local rotation( helical )', client.GetSegmentLocalRotationHelical( subjectName, segmentName ) )               
                    #print( segmentName, 'has local rotation( EulerXYZ )', client.GetSegmentLocalRotationEulerXYZ( subjectName, segmentName ) )               
                    #print( segmentName, 'has local rotation( Quaternion )', client.GetSegmentLocalRotationQuaternion( subjectName, segmentName ) )               
                    #print( segmentName, 'has local rotation( Matrix )', client.GetSegmentLocalRotationMatrix( subjectName, segmentName ) )
            objects_data_json = json.dumps(objects_data)
            emit('vicondata', objects_data_json)
    except ViconDataStream.DataStreamException as e:
        print( 'Error', e )
    # emit('vicondata')

if __name__ == '__main__':
   socketio.run(app)