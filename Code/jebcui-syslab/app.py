from flask import Flask, render_template
from vicon_dssdk import ViconDataStream
from flask_socketio import SocketIO, emit

import time
import json

client = ViconDataStream.Client()
frames = []
print( 'Connecting' )

'''
while not client.IsConnected():
    print( '.' )
    client.Connect( '192.168.69.2:801' )
    time.sleep(1)
    print(client.GetFrame())
client.EnableSegmentData()
'''

app = Flask(__name__)
socketio = SocketIO(app)

@app.route("/")
def index():
    return render_template('index.html')

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