import vectormath as vmath
import math
import numpy as np
from pyquaternion import Quaternion
import logging

ON_STRING = 1
# Off the string and below at least one stick
OFF_STRING_LOOSE = 2
# Off the string and above the sticks
FLYING = 3
# Outside the border of the ellipse. Requires position correction
OUTSIDE_STRING = 4

class DiaboloSimConfig():
    '''
    geometry_msgs/PoseArray initial_poses # Initial positions of diabolo [0], stick_left [1] and stick_right[2]
    float32 rot_velocity # Rotational velocity of the diabolo
    geometry_msgs/Point trans_velocity # Translation velocity of the diabolo (world frame)
    float32 pv_pre_cap_scale # pv = pull velocity
    float32 pv_post_cap_scale
    float32 pv_cap_scale
    float32 velocity_diffusion_factor # The factor by which the velocity reduces every time step
    float32 time_step # The length of a time step
    bool caps_valid # Set to true if want to change the pv scaling factors
    float32 mass # Mass of the diabolo. Ignored if 0
    float32 axle_radius # Radius of the diabolo axle
    float32 string_length # Ignored if 0 or less than initial distance between strings
    string file_name # This is the name of the experiment file. 
    '''
    def __init__(self,
            initial_poses,
            rot_velocity,
            trans_velocity,
            pv_pre_cap_scale,
            pv_post_cap_scale,
            pv_cap_scale,
            velocity_diffusion_factor,
            time_step,
            caps_valid,
            mass,
            axle_radius,
            string_length,
            file_name
        ):
        self.initial_poses = initial_poses
        self.rot_velocity = rot_velocity
        self.trans_velocity = trans_velocity
        self.pv_pre_cap_scale = pv_pre_cap_scale
        self.pv_post_cap_scale = pv_post_cap_scale
        self.pv_cap_scale = pv_cap_scale
        self.velocity_diffusion_factor = velocity_diffusion_factor
        self.time_step = time_step
        self.caps_valid = caps_valid
        self.mass = mass
        self.axle_radius = axle_radius
        self.string_length = string_length
        self.file_name = file_name

    def __str__(self):
        output = ""
        output += str(self.initial_poses)
        output += " "+str(self.rot_velocity)
        output += " "+str(self.trans_velocity)
        output += " "+str(self.pv_pre_cap_scale)
        output += " "+str(self.pv_post_cap_scale)
        output += " "+str(self.pv_cap_scale)
        output += " "+str(self.velocity_diffusion_factor)
        output += " "+str(self.time_step)
        output += " "+str(self.caps_valid)
        output += " "+str(self.mass)
        output += " "+str(self.axle_radius )
        output += " "+str(self.string_length)
        output += " "+str(self.file_name)
        return output

# PoseArray -> variable poses that is an array of Pose's
# Pose -> variable position is a point (x,y,z) and orientation is a quaternion (x,y,z,w)

class PoseArray():
    # poses is a list of Pose objects
    def __init__(self, poses):
        self.poses = poses
    
    def __str__(self):
        return str([str(pose) for pose in self.poses])

class Pose():
    # position is a Vector3 object
    # quaternion is a Quaternion object
    def __init__(self, position, quaternion):
        self.position = position
        self.quaternion = quaternion

    def __str__(self):
        return f"{self.quaternion} {self.position}"

class MyQuaternion(Quaternion):
    @property
    def w(self):
        return self.q[0]
    @w.setter
    def w(self, value):
        self.q[0] = value
    @property
    def x(self):
        return self.q[1]
    @x.setter
    def x(self, value):
        self.q[1] = value
    @property
    def y(self):
        return self.q[2]
    @y.setter
    def y(self, value):
        self.q[2] = value
    @property
    def z(self):
        return self.q[3]
    @z.setter
    def z(self, value):
        self.q[3] = value

    def toEuler(self):
        # roll (x-axis rotation)
        sinr_cosp = 2 * (self.w * self.x + self.y * self.z)
        cosr_cosp = 1 - 2 * (self.x * self.x + self.y * self.y)
        roll = math.atan2(sinr_cosp, cosr_cosp)

        # pitch (y-axis rotation)
        sinp = 2 * (self.w * self.y - self.z * self.x)
        if (abs(sinp) >= 1):
            pitch = math.copysign(math.pi / 2, sinp) # use 90 degrees if out of range
        else:
            pitch = math.asin(sinp)

        # yaw (z-axis rotation)
        siny_cosp = 2 * (self.w * self.z + self.x * self.y)
        cosy_cosp = 1 - 2 * (self.y * self.y + self.z * self.z)
        yaw = math.atan2(siny_cosp, cosy_cosp)

        return (roll, pitch, yaw)

class DiaboloState():
    ON_STR=1
    OFF_STR_LOOSE=2
    FLY=3
    OUTSIDE_STR=4
    def __init__(self,
        pose,
        trans_velocity,
        rot_velocity,
        mass,
        string_length,
        string_state
    ):
        self.pose = pose
        self.trans_velocity = trans_velocity
        self.rot_velocity = rot_velocity
        self.mass = mass
        self.string_length = string_length
        self.string_state = string_state
        
    def __str__(self):
        output = ""
        output += str(self.pose)
        output += " "+str(self.trans_velocity)
        output += " "+str(self.rot_velocity)
        output += " "+str(self.mass)
        output += " "+str(self.string_length)
        output += " "+str(self.string_state)
        return output

class Transform():
    def __init__(self, m_basis=None, m_origin=None):
        self.m_basis = m_basis
        self.m_origin = m_origin
    
    # other is a vmath.Vector3 vector
    def __mul__(self, other):
        #self.logger.debug('__mul__')
        # matrix multiplication of m_basis with other
        dot_product = vmath.Vector3(np.dot(self.m_basis, other))
        # Then add result ot m_origin
        output = dot_product + self.m_origin
        return output

    def inverse(self):
        inv = self.m_basis.T
        return Transform(inv, np.dot(inv, -self.m_origin))
    
    def setOrigin(self, origin):
        self.m_origin = origin

    def setRotation(self, q):
        self.m_basis = q.rotation_matrix

    def getRotation(self):
        return MyQuaternion(matrix = self.m_basis)

class DiaboloPredictor():
    gravity_ = vmath.Vector3(0,0,-9.8)
    logging.basicConfig(filename="console.log",format='%(asctime)s %(message)s',filemode='w')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # initial_state is a DiaboloSimConfig object
    def __init__(self, initial_state):
        # intilize the variables that are in the h file but not in the init method
        self.ellipse_transform_ = Transform()
        self.diabolo_transform_ = Transform()

        # initialize all the instance variables
        self.initial_state_ = initial_state
        
        # stick positions
        self.left_stick_last_position_ = initial_state.initial_poses.poses[1].position
        self.right_stick_last_position_ = initial_state.initial_poses.poses[2].position
        self.left_stick_current_position_ = self.left_stick_last_position_
        self.right_stick_current_position_ = self.right_stick_last_position_

        # diabolo data
        # diabolo position
        self.diabolo_last_position_ = initial_state.initial_poses.poses[0].position
        self.diabolo_current_position_ = self.diabolo_last_position_
        self.logger.debug(f"Initial diabolo position = {self.diabolo_current_position_}")
        # diabolo attributes
        self.diabolo_last_state_ = OFF_STRING_LOOSE
        self.diabolo_state_ = 0
        self.diabolo_current_velocity_ = initial_state.trans_velocity
        self.diabolo_current_rot_velocity_ = initial_state.rot_velocity
        
        # factors
        self.pv_pre_cap_scaling_factor_ = initial_state.pv_pre_cap_scale
        self.pv_post_cap_scaling_factor_ = initial_state.pv_post_cap_scale
        self.pv_cap_scaling_factor_ = initial_state.pv_cap_scale

        self.velocity_diffusion_factor_ = initial_state.velocity_diffusion_factor

        # constants
        self.time_step_ = initial_state.time_step
        self.string_length_ = initial_state.string_length
        self.diabolo_axle_radius_ = initial_state.axle_radius
        self.catching_string_taut_tolerance_ = 0.03
        self.pv_string_taut_tolerance_ = 0.03
        self.rot_friction_factor_ = 0.00015

        # constrain 2D?
        self.constrain_to_2D_flag = False
        self.plane_point_2D = vmath.Vector3()
        self.plane_normal_2D = vmath.Vector3()
        # self.get_ros_parameters()

        self.sleep_flag_ = False

    def predict(self, left_poses, right_poses, stick_time_step):
        predicted_states = []
        left_times = [stick_time_step]
        right_times = [stick_time_step]
        return self.predict_(left_poses, right_poses, left_times, right_times, predicted_states, False)

    def predict(self, left_poses, right_poses, left_times, right_times, predicted_states, store_states):
        # Store first state in predicted states
        ds_inital = DiaboloState(
            Pose(self.diabolo_current_position_, MyQuaternion()),
            self.diabolo_current_velocity_,
            self.diabolo_current_rot_velocity_,
            0,
            self.string_length_,
            self.diabolo_state_
        )

        if (store_states):
            predicted_states.append(ds_inital)

        self.logger.debug(f"First diabolo state position = {ds_inital.pose}")

        self.logger.debug("Starting prediction trial")
        self.run_prediction_trial(left_poses, right_poses, left_times, right_times, predicted_states, store_states)
        self.logger.debug("Finished prediction trial")

        # Resulting diabolo state from trial
        ds = DiaboloState(
            Pose(self.diabolo_current_position_, MyQuaternion()), 
            self.diabolo_current_velocity_,
            self.diabolo_current_rot_velocity_,
            0,
            self.string_length_,
            self.diabolo_state_
        )

        return ds

    def get_current_state(self):
        ds = DiaboloState(Pose(None, None),None,0,0,0,0)
        # Position values
        ds.pose.position = self.diabolo_current_position_

        # Translational velocity
        ds.trans_velocity = self.diabolo_current_velocity_
        ds.string_length = self.string_length_

        # Rotational velocity
        ds.rot_velocity = self.diabolo_current_rot_velocity_

        return ds

    def get_current_state_full(self):
        cs = DiaboloSimConfig(PoseArray(None), 0, None, 0, 0, 0, 0, 0, False, 0, 0, 0, '')
        cs.initial_poses.poses = [None,None,None]

        cs.initial_poses.poses[0].position = self.diabolo_current_position_
        cs.initial_poses.poses[1].position = self.left_stick_current_position_
        cs.initial_poses.poses[2].position = self.right_stick_current_position_

        # Translational velocity
        cs.trans_velocity = self.diabolo_current_velocity_

        # Rotational velocity
        cs.rot_velocity = self.diabolo_current_rot_velocity_

        # Simulation parameters
        cs.string_length = self.string_length_
        cs.pv_pre_cap_scale = self.pv_pre_cap_scaling_factor_
        cs.pv_post_cap_scale = self.pv_post_cap_scaling_factor_
        cs.pv_cap_scale = self.pv_cap_scaling_factor_
        cs.velocity_diffusion_factor = self.velocity_diffusion_factor_
        cs.time_step = self.time_step_
        cs.string_length = self.string_length_
        cs.axle_radius = self.diabolo_axle_radius_

        return cs

    def run_prediction_trial(self, left_poses, right_poses, left_times, right_times, predicted_states, store_states):  
        left_poses_counter = 0
        right_poses_counter = 0
        current_sim_time = 0
        # diabolo_state_counter = 1  # The initial state is already put in the predicted states array
        # The trajectories do not start with 0 time
        # To get the interpolated stick positions between 0 and the first stick position, the following are used
        # last_left_time = 0
        # last_right_time = 0
        # next_left_time = left_times[0]
        # next_right_time = right_times[0]
        while left_poses_counter < len(left_times) or right_poses_counter < len(right_times): # Run prediction trial for all poses
            if current_sim_time > left_times[left_poses_counter] and left_poses_counter < len(left_times):
            # Set left stick to the next pose point
                # last_left_time = left_times[left_poses_counter]
                self.left_stick_current_position_ = left_poses.poses[left_poses_counter].position
                left_poses_counter+=1
                # next_left_time = left_times[left_poses_counter]

                left_stick_current_position_ = self.left_stick_current_position_
                if left_stick_current_position_.x < 0.01:  # For debugging (sanity check)
                    self.logger.debug("x value < 0.01, not normal for the robot. POSE IS LIKELY CORRUPT!")
                    self.logger.debug(f"left_stick_current_position_ set to = {left_stick_current_position_}")
                    self.logger.debug(f"left_poses_counter = {left_poses_counter}")

            if current_sim_time > right_times[right_poses_counter] and right_poses_counter < len(right_times):
            # Set right stick to the next pose point
                # right_left_time = right_times[right_poses_counter]
                self.right_stick_current_position_ = right_poses.poses[right_poses_counter].position
                right_poses_counter+=1
                # next_right_time = right_times[right_poses_counter]

                right_stick_current_position_ = self.right_stick_current_position_
                if right_stick_current_position_.x < 0.01:  # For debugging (sanity check)
                    self.logger.debug("x value < 0.01, not normal for the robot. POSE IS LIKELY CORRUPT!")
                    self.logger.debug(f"right_stick_current_position_ set to = {right_stick_current_position_}")
                    self.logger.debug(f"right_poses_counter = {right_poses_counter}")

            self.step()
            current_sim_time += self.time_step_
            # Store all diabolo states if store_states is true
            if store_states:
                pose = Pose(self.diabolo_current_position_, MyQuaternion())

                velocity = self.diabolo_current_velocity_

                rot_velocity = self.diabolo_current_rot_velocity_
                string_length = self.string_length_
                string_state = self.diabolo_state_

                ds = DiaboloState(pose, velocity, rot_velocity, 0, string_length, string_state)
                predicted_states.append(ds)
                # diabolo_state_counter+=1

            # TEMPORARY: Remove after debug
            # What is the point of this section
            self.marker_count_ = 0
            if self.sleep_flag_:
                self.publish_visualization_markers()
                # ros::Duration(this->time_step_ / 2.0).sleep();
            # End of temporary

            self.right_stick_last_position_ = self.right_stick_current_position_
            self.left_stick_last_position_ = self.left_stick_current_position_
  
        # Erase the empty elements in the predicted states vector
        if store_states:
            # predicted_states.erase(predicted_states.begin() + diabolo_state_counter, predicted_states.end());
            pass
        # ROS_WARN_STREAM("Predicted states vector size = " << predicted_states.size());


    def set_2D_constraint(self, plane_normal, plane_point):
        self.constrain_to_2D_flag = True
        self.plane_normal_2D = plane_normal
        self.plane_normal_2D = self.plane_normal_2D.normalize()

        self.plane_point_2D = plane_point

    def remove_2D_constraint(self):
        self.constrain_to_2D_flag = False

    # What is this method supposed to do (I dont use this)
    def get_ros_paramters(self):
        if not self.n_.getParam("/constrain_diabolo_2D", self.constrain_to_2D_flag):
            self.constrain_to_2D_flag = False;  # False by default
        else:
            if self.constrain_to_2D_flag:
                p_normal = None
                p_point = None
                self.logger.debug("Constraining diabolo motion to 2D")
                if not self.n_.getParam("/diabolo_2D_plane_normal", p_normal):  # This is a double vector
                    self.logger.debug("2D plane normal not set. Defaulting to world x-axis")
                    p_normal.clear()
                    p_normal.push_back(1.0)
                    p_normal.push_back(0.0)
                    p_normal.push_back(0.0)
                if not self.n_.getParam("/diabolo_2D_plane_point", p_point):  # This is a double vector
                    self.logger.debug("Point on 2D plane not set. Defaulting to (0.7,0,0)")
                    p_point.clear()
                    p_point.push_back(0.7)
                    p_point.push_back(0.0)
                    p_point.push_back(0.0)

                self.plane_normal_2D = vmath.Vector3((p_normal.at(0)), (p_normal.at(1)), (p_normal.at(2)))
                self.plane_normal_2D = self.plane_normal_2D.normalize()
                self.plane_point_2D = vmath.Vector3((p_point.at(0)), (p_point.at(1)), (p_point.at(2)))

    def IsFinite(self, position):
        return True

    def step(self):
        # This step replaces gazebo's internal velocity and acceleration calculation
        # It treats the diabolo like a free body without constraints under gravity_
        self.perform_freebody_calculation()
        self.ellipse_current_velocity_ = self.get_ellipse_velocity()

        if self.constrain_to_2D_flag:
            self.diabolo_current_position_, self.diabolo_current_velocity_ = \
                self.constrain_to_2D(self.diabolo_current_position_, self.diabolo_current_velocity_)
        # Store information about current ellipse
        self.store_ellipse_axes_lengths()
        # Store current ellipse transform
        self.store_ellipse_transform()
        pose = Pose(self.diabolo_current_position_, MyQuaternion())
        self.store_diabolo_transform(pose)

        # Get the diabolo state
        self.diabolo_state_ = self.get_diabolo_state()

        if self.diabolo_state_ == OUTSIDE_STRING:
            diabolo_new_position_ = self.constrain_diabolo_position()
            if not self.IsFinite(diabolo_new_position_): #create a IsFinite function
                self.logger.debug("Constrained position is not finite. Not changing")
                diabolo_new_position_ = self.diabolo_current_position_

            # Get the max pull velocity
            pull_velocity_cap = self.get_pull_velocity_cap()
            # Calculate the pull velocity using the new position and the old position
            self.pull_velocity_ = self.get_pull_velocity(self.diabolo_current_position_, diabolo_new_position_)

            self.diabolo_current_position_ = diabolo_new_position_
            # Add the pull velocity to the current diabolo velocity

            # Make pull velocity for this time step 0 if it is not directed towards the center of the ellipse
            if not self.pull_velocity_is_directed_inward():
                self.pull_velocity_ = vmath.Vector3(0,0,0)

            if self.pull_velocity_.length > pull_velocity_cap.length:
                self.pull_velocity_ = pull_velocity_cap
            if self.pull_velocity_.length > 0.0:
                ellipse_y_axis = self.left_stick_current_position_ - self.right_stick_current_position_
                distance_between_sticks = (ellipse_y_axis).length
                if self.string_length_ - self.pv_string_taut_tolerance_ <= distance_between_sticks:
                    self.pull_velocity_ = self.apply_edge_case_pv_constraint(self.pull_velocity_)

            self.pull_velocity_ = self.pull_velocity_ * self.pv_post_cap_scaling_factor_

            # Remove the positive component of the diabolo's velocity along the
            # positive direction of the surface normal of the ellipse

            self.diabolo_current_velocity_ = self.constrain_diabolo_velocity(
                self.diabolo_current_velocity_ * self.velocity_diffusion_factor_ + self.pull_velocity_)
            if self.diabolo_last_state_ == ON_STRING or self.diabolo_last_state_ == OUTSIDE_STRING:
                self.diabolo_current_rot_velocity_ += self.get_rot_velocity_change()

        self.diabolo_last_position_ = self.diabolo_current_position_
        self.diabolo_last_state_ = self.diabolo_state_

    # only the publish methods and constrain_diabolo_position use the store transform values
    def store_ellipse_transform(self):
        ellipse_y_axis = self.left_stick_current_position_ - self.right_stick_current_position_
        distance_between_focii = ellipse_y_axis.length
        ellipse_y_axis = ellipse_y_axis.normalize()
        y_axis = vmath.Vector3(0, 1, 0)
        rotation_axis = y_axis.cross(ellipse_y_axis)
        rotation_axis = rotation_axis.normalize()

        # This is the cosine of the angle between the y axis (world frame) and the y
        # axis of the ellipse
        rotation_angle = y_axis.dot(ellipse_y_axis)

        q = MyQuaternion(axis=rotation_axis, radians = math.acos(rotation_angle))

        center = self.left_stick_current_position_ + self.right_stick_current_position_
        center /= 2.0

        self.ellipse_transform_.setOrigin(center) # self.ellipse_transform_: tf::Transform
        self.ellipse_transform_.setRotation(q)

    def store_ellipse_axes_lengths(self):
        between_focii = self.left_stick_current_position_ - self.right_stick_current_position_
        distance_between_focii = between_focii.length

        self.ellipse_major_axis_length_ = self.string_length_ / 2.0 # From definition of ellipse
        self.ellipse_minor_axis_length_ = math.sqrt(math.pow(self.ellipse_major_axis_length_, 2.0) - math.pow((distance_between_focii / 2.0), 2.0))

    def get_ellipse_velocity(self):
        last_origin = (self.left_stick_last_position_ + self.right_stick_last_position_) / 2.0
        current_origin = (self.left_stick_current_position_ + self.right_stick_current_position_) / 2.0

        velo = (current_origin - last_origin) / self.time_step_

        return velo

    def constrain_to_2D(self, pos, vel): # Fixed this method to overcome the python argument issue
        # This function constrains the diabolo position and velocity to the desired 2D plane
        pos = self.constrain_position_to_2D(pos)
        vel = self.constrain_velocity_to_2D(vel)
        return pos, vel

    def constrain_position_to_2D(self, pos):
        # This function projects the diabolo position onto the set 2D plane
        # new_pos = old_pos - projection of (old_pos - plane_point) on the plane normal
        # projection of (old_pos - plane_point) on the plane normal = p_c_normal
        p_c_normal = pos - self.plane_point_2D # Intermediate step
        
        p_c_normal = p_c_normal.dot(self.plane_normal_2D) * self.plane_normal_2D

        return pos - p_c_normal

    def constrain_velocity_to_2D(self, vel):
        # This function constrains the velocity vel to be parallel to the plane, by removing its component parallel to the
        # plane normal

        return vel - vel.dot(self.plane_normal_2D) * self.plane_normal_2D

    def get_diabolo_state(self):
        # Description:
        # The diabolo has 4 possible states: ON_STRING, OUTSIDE_STRING, OFF_STRING_LOOSE, FLYING
        # ON_STRING: The diabolo is exactly on the string. This state is rare
        # OFF_STRING_LOOSE: The diabolo is off the string, but not so far off that it cannot be caught easily
        #                  i.e. This is when the diabolo jumps, but does not pass the plane containing the y-axis of the
        #                  ellipse and the cross product of the Z-axis in the world frame and the y-axis of the ellipse,
        #                  passing through the stick tip positions
        # FLYING: The diabolo has left the string and crossed the plane described above
        # OUTSIDE_STRING: This is when the diabolo needs to be constrained to the ellipse
        # Transitions
        # Allowed transitions: ON_STRING -> OFF_STRING_LOOSE, OFF_STRING_LOOSE -> ON_STRING, ON_STRING -> FLYING,
        # OFF_STRING_LOOSE -> FLYING FLYING -> ON_STRING is allowed ONLY if the string is (close to) taut
        distance_between_sticks = np.linalg.norm(self.left_stick_current_position_ - self.right_stick_current_position_)

        string_taut_flag = False
        if self.string_length_ - self.catching_string_taut_tolerance_ <= distance_between_sticks:
            string_taut_flag = True
            self.logger.debug("String is taut enough to catch diabolo")

        distance_to_stick_1 = np.linalg.norm(self.diabolo_current_position_ - self.left_stick_current_position_)
        distance_to_stick_2 = np.linalg.norm(self.diabolo_current_position_ - self.right_stick_current_position_)
        distance_to_sticks = distance_to_stick_1 + distance_to_stick_2
        ########## Start check if diabolo is flying

        # Get normal to the plane containing the ellipse y axis in the world frame and the world frame x axis
        ellipse_y_axis = self.left_stick_current_position_ - self.right_stick_current_position_
        plane_normal = None
        if ellipse_y_axis.cross(vmath.Vector3(1.0, 0.0, 0.0)).length == 0.:
            # If the ellipse is y-axis is parallel to the ground
            # If ellipse y axis parallel to world x axis, plane normal is straight up
            plane_normal = vmath.Vector3(0.0, 0.0, 1.0)
        
        # Otherwise,
        # The normal to this plane is e_t x (e_z x z_world) where ey = ellipse y axis in world frame, z_world = world frame z
        # axis The diabolo changes to state flying if it is "above" this plane
        else:
            plane_normal = vmath.Vector3(1.0, 0.0, 0.0).cross(ellipse_y_axis)

        plane_normal = plane_normal.normalize()
        # Get the vector from the ellipse center to the diabolo position in the world frame
        # d_ellipse = d_world - e_world
        ellipse_to_diabolo_vec = self.diabolo_current_position_ -\
            (self.left_stick_current_position_ + self.right_stick_current_position_) / 2.0
        ellipse_to_diabolo_vec = ellipse_to_diabolo_vec.normalize()
        # If the dot product of this vector and the plane_normal > 0.0, the diabolo is FLYING
        check_val = ellipse_to_diabolo_vec.dot(plane_normal)
        if check_val > 0.0 and self.diabolo_between_sticks() and \
            (self.diabolo_current_position_.z > self.left_stick_current_position_.z or \
            self.diabolo_current_position_.z > self.right_stick_current_position_.z):
            return FLYING
        # This is the edge case, when the ellipse is close to a line
        if string_taut_flag:
            if self.diabolo_last_state_ == FLYING: # Can transition to OFF_STRING_LOOSE if string is taut
                # Check if the diabolo is between the stick tips
                if self.diabolo_between_sticks():
                    # Check if diabolo is close enough to the line between sticks
                    # Get distance from diabolo to line between stick tips
                    center_to_diabolo = \
                        self.diabolo_current_position_ - \
                        (self.left_stick_current_position_ + self.right_stick_current_position_) / 2.0
                    axis_to_diabolo = \
                        center_to_diabolo - center_to_diabolo.dot(ellipse_y_axis.normalize()) * ellipse_y_axis.normalize()
                    diabolo_distance_to_axis = axis_to_diabolo.length
                    if diabolo_distance_to_axis < 0.1:  # Catch if distance to the axis is less than 10 cm
                        return OFF_STRING_LOOSE
                    else:
                        self.logger.debug(f"Unable to catch diabolo. Distance to string = {diabolo_distance_to_axis}")
        
        if (self.string_length_ - (distance_to_sticks)) > 0.:  # The diabolo is not on the string, but it is not flying
            if self.diabolo_last_state_ != FLYING:
                return OFF_STRING_LOOSE;  # The diabolo has just "hopped" off the string. It can still get back on the string
                                          # without the string being taut
            else:
                return FLYING

        elif (distance_to_sticks - self.string_length_) > 0.:   # The string is taut and the diabolo needs position
                                                                # correction
            # First the case if the last state was OFF_STRING_LOOSE
            if self.diabolo_last_state_ != FLYING:
                # Can transition to OUTSIDE_STRING state in this case
                return OUTSIDE_STRING
            else:
                return FLYING

        return ON_STRING

    def diabolo_between_sticks(self):
        left_stick_to_diabolo = None
        right_stick_to_diabolo = None
        left_stick_to_diabolo = self.left_stick_current_position_ - self.diabolo_current_position_
        right_stick_to_diabolo = self.right_stick_current_position_ - self.diabolo_current_position_

        prod = left_stick_to_diabolo.dot(right_stick_to_diabolo)

        if prod > 0:
            return False

        if prod <= 0:
            return True

    # This requires a Transform object
    def constrain_diabolo_position(self):
        # Use parametric equation of ellipse
        # Calculate angles made with axes and solve for distance from center. Then
        # find new coordinates
        # Angle with z axis: phi
        # Angle with x axis: theta

        world_frame_pos = self.diabolo_current_position_

        ellipse_frame_pos = self.ellipse_transform_.inverse() * world_frame_pos

        ellipse_frame_pos_vector = ellipse_frame_pos

        world_position = None

        # Angle with xy plane
        if np.all((ellipse_frame_pos_vector==0)):
            new_ellipse_frame_pos = vmath.Vector3(0, 0, 0)
            world_frame_pos = self.ellipse_transform_ * new_ellipse_frame_pos

            world_position = world_frame_pos
        else:
            cos_phi = ellipse_frame_pos_vector.z / \
                    math.sqrt(math.pow(ellipse_frame_pos_vector.x, 2.0) + math.pow(ellipse_frame_pos_vector.y, 2.0) + \
                    math.pow(ellipse_frame_pos_vector.z, 2.0))
            sin_phi = math.sqrt(math.pow(ellipse_frame_pos_vector.x, 2.0) + math.pow(ellipse_frame_pos_vector.y, 2.0)) / \
                    math.sqrt(math.pow(ellipse_frame_pos_vector.x, 2.0) + math.pow(ellipse_frame_pos_vector.y, 2.0) + \
                    math.pow(ellipse_frame_pos_vector.z, 2.0))

            length = (math.sqrt(math.pow(ellipse_frame_pos_vector.x, 2.0) + math.pow(ellipse_frame_pos_vector.y, 2.0)))
            new_x_ellipse_frame = None
            new_y_ellipse_frame = None
            new_z_ellipse_frame = None
            r = None
            if not length == 0.0:
                cos_theta = ellipse_frame_pos_vector.x / \
                             (math.sqrt(math.pow(ellipse_frame_pos_vector.x, 2.0) + math.pow(ellipse_frame_pos_vector.y, 2.0)))
                sin_theta = ellipse_frame_pos_vector.y / \
                                    (math.sqrt(math.pow(ellipse_frame_pos_vector.x, 2.0) + math.pow(ellipse_frame_pos_vector.y, 2.0)))

                r = math.sqrt(1.0 / ((math.pow(cos_theta, 2.0) * math.pow(sin_phi, 2.0)) / math.pow(self.ellipse_minor_axis_length_, 2.0) + \
                                (math.pow(sin_theta, 2.0) * math.pow(sin_phi, 2.0)) / math.pow(self.ellipse_major_axis_length_, 2.0) + \
                                (math.pow(cos_phi, 2.0)) / math.pow(self.ellipse_minor_axis_length_, 2.0)))

                # New position of diabolo
                new_x_ellipse_frame = r * cos_theta * sin_phi
                new_y_ellipse_frame = r * sin_theta * sin_phi
                new_z_ellipse_frame = r * cos_phi
            else:
                r = self.ellipse_minor_axis_length_
                new_x_ellipse_frame = 0.
                new_y_ellipse_frame = 0.
                new_z_ellipse_frame = r * cos_phi
            
            new_ellipse_frame_pos = vmath.Vector3(new_x_ellipse_frame, new_y_ellipse_frame, new_z_ellipse_frame)
            world_frame_pos = self.ellipse_transform_ * new_ellipse_frame_pos

            world_position = world_frame_pos

        return world_position

    def get_pull_velocity_cap(self):
        # This cap is 0 in some cases, so this function determines
        # if the pull velocity is applied at all.
        # The cap is 0 e.g. when the sticks are moving in the same direction as the diabolo

        origin_velocity_cap = None
        minor_axis_cap = None
        # Initially get the vector along which the pull velocity will be directed.
        # It is from the current diabolo position to the center of the ellipse
        current_center = \
            (self.left_stick_current_position_ + self.right_stick_current_position_) / 2.0
        last_center = (self.left_stick_last_position_ + self.right_stick_last_position_) / 2.0
        direction_vector = self.get_ellipse_normal_in_world_frame(self.diabolo_current_position_)
        direction_vector = direction_vector.normalize()
        direction_vector = -direction_vector
        ellipse_origin_change = current_center - last_center

        if direction_vector.dot(ellipse_origin_change) > 0.0:   # If the change in origin velocity has a positive component
                                                                # along the direction_vector direction
            origin_velocity_cap = direction_vector * (ellipse_origin_change.length / self.time_step_)
        else:
            origin_velocity_cap = vmath.Vector3(0, 0, 0)

        # Now get the velocity due to the change of length of the minor axis
        last_minor_axis = \
            self.get_ellipse_minor_axis_length(self.left_stick_last_position_, self.right_stick_last_position_)
        current_minor_axis = \
            self.get_ellipse_minor_axis_length(self.left_stick_current_position_, self.right_stick_current_position_)

        if current_minor_axis <= last_minor_axis: # If the minor axis length has decreased
            minor_axis_cap = direction_vector * ((last_minor_axis - current_minor_axis) / self.time_step_)
        else:
            minor_axis_cap = vmath.Vector3(0, 0, 0)

        return (origin_velocity_cap + minor_axis_cap) * self.pv_cap_scaling_factor_

    def get_ellipse_minor_axis_length(self, foci_1, foci_2):
        between_focii = foci_1 - foci_2
        distance_between_focii = between_focii.length

        major_axis_length = self.string_length_ / 2.0;  # From definition of ellipse
        minor_axis_length_ = math.sqrt(math.pow(major_axis_length, 2.0) - math.pow((distance_between_focii / 2.0), 2.0))

        return minor_axis_length_

    def get_ellipse_normal_in_world_frame(self, world_frame_pos_vec):
        world_frame_pos = world_frame_pos_vec

        ellipse_frame_pos = self.ellipse_transform_.inverse() * world_frame_pos

        # Get normal to ellipse at diabolo's location

        ellipse_frame_normal = vmath.Vector3(
            2.0 * (ellipse_frame_pos.x / self.ellipse_minor_axis_length_), 
            2.0 * (ellipse_frame_pos.y / self.ellipse_major_axis_length_),  # major axis is aligned along y direction
            2.0 * (ellipse_frame_pos.z / self.ellipse_minor_axis_length_)
        )

        ellipse_frame_normal = ellipse_frame_normal.normalize()

        # Want only the rotation (not the position) transform of the normal vector
        # Using quaternion rotation
        # v_new_as_quat = Q * v_old_as_quat * Q_inverse
        # does not work: need to implement quaternion methods
        ellipse_to_world_rot = self.ellipse_transform_.getRotation() # Rotation to rotate from ellipse frame to world frame
        ellipse_frame_normal_as_quat = MyQuaternion(ellipse_frame_normal.x, ellipse_frame_normal.y,
                                                    ellipse_frame_normal.z, 0.0)

        # Using quaternion rotataion identity v' = qvq*
        world_frame_normal_as_quat = ellipse_to_world_rot * ellipse_frame_normal_as_quat
        world_frame_normal_as_quat = world_frame_normal_as_quat * ellipse_to_world_rot.inverse

        # Ignoring the w term gives us the new vector
        world_frame_normal_vector = vmath.Vector3(
            world_frame_normal_as_quat.x, world_frame_normal_as_quat.y, world_frame_normal_as_quat.z)
        return world_frame_normal_vector.normalize()

    def get_pull_velocity(self, old_position, new_position):
        v_pull = new_position - old_position
        v_pull = v_pull / self.time_step_
        normal_dir = self.get_ellipse_normal_in_world_frame(new_position)
        normal_dir = -normal_dir
        v_pull = v_pull.dot(normal_dir) * normal_dir * self.pv_pre_cap_scaling_factor_
        return v_pull

    def pull_velocity_is_directed_inward(self):
        # Get position of ellipse center in world frame
        # Get vector from diabolo to ellipse center
        # Find dot product of calculated pull velocity and the above vector.
        # Return false if dot product is negative, and true if positive

        center = (self.left_stick_current_position_ + self.right_stick_current_position_) / 2.0
        direction_vector = center - self.diabolo_current_position_

        dot_product = direction_vector.dot(self.pull_velocity_)
        if dot_product >= 0:
            return True
        else:
            return False

    # Fix issues relating to python argumenting passing
    def apply_edge_case_pv_constraint(self, v_pull):
        # This is used when the sticks are close to taut, and the ellipse is very thin.
        # Throwing the diabolo in 3D can cause the diabolo to be pulled forward/backward relative to the player,
        # as the curvature changes 

        ellipse_y_axis = self.left_stick_current_position_ - self.right_stick_current_position_
        # Get normal to the plane containing ellipse y axis and world z axis
        normal = ellipse_y_axis.cross(vmath.Vector3(0.0, 0.0, 1.0))
        normal = normal.normalize()
        v_pull_mag = v_pull.length
        # Get component of the pull velocity in the direction of the normal
        v_pull_in_normal_direction = v_pull.dot(normal) * normal
        return (v_pull - v_pull_in_normal_direction).normalize() * v_pull_mag; # keep the magnitude of the pull velocity

    def constrain_diabolo_velocity(self, diabolo_velocity):
        world_frame_normal_vector = self.get_ellipse_normal_in_world_frame(self.diabolo_current_position_)

        new_velocity = None
        velocity_in_normal_dir = None
        speed_in_normal_dir = diabolo_velocity.dot(world_frame_normal_vector)
        if speed_in_normal_dir > 0.0:   # If the diabolo velocity has a positive
                                        # component in the direction of the surface
                                        # normal
            # Project the velocity along the tangent to the ellipse
            velocity_in_normal_dir = world_frame_normal_vector * speed_in_normal_dir
            new_velocity = diabolo_velocity - velocity_in_normal_dir
        else:
            # If the component of diabolo velocity in the direction of the ellipse
            # normal is negative, no change
            new_velocity = diabolo_velocity
        return new_velocity

    def get_rot_velocity_change(self):
        # The length of string that moved past the diabolo in the last time step
        old_dist_to_right_stick = np.linalg.norm(self.right_stick_last_position_-self.diabolo_last_position_)
        new_dist_to_right_stick = np.linalg.norm(self.right_stick_current_position_ - self.diabolo_current_position_)

        string_velo = (new_dist_to_right_stick - old_dist_to_right_stick) / (self.time_step_)
        # This is the speed of the diabolo axle at axle_radius distance from the center
        axle_velo = self.diabolo_current_rot_velocity_ * self.diabolo_axle_radius_

        return (((string_velo - axle_velo) * self.rot_friction_factor_) / self.diabolo_axle_radius_)

    def perform_freebody_calculation(self):
        self.diabolo_current_position_ = self.diabolo_current_position_ +\
                                         self.diabolo_current_velocity_ * self.time_step_ +\
                                         self.gravity_ * self.time_step_ * self.time_step_ * 0.5

        self.diabolo_current_velocity_ = self.diabolo_current_velocity_ + self.gravity_ * self.time_step_

    # only the publish methods use the store transform values
    def store_diabolo_transform(self, pose_):
        self.diabolo_transform_.setOrigin(pose_.position) # diabolo_transform_: tf::Transform
        self.diabolo_transform_.setRotation(pose_.quaternion)