This directory contains the original work of transpiling the diabolo predictor in diabolo_motion_generator.cpp to python.

The code from von Drigalski et al.'s diabolo repository:
There are two classes in diabolo_motion_generator.cpp (the quotes are von Drigalski et al.'s words):
1. DiaboloMotionGenerator line 10 – line 945: This “generates a stick trajectory for the desired diabolo trajectory using a random walk”
1. DiaboloPredictor line 946 – end: This is “used to obtain the state of the diabolo at the next time step, given the current diabolo state and stick positions.”

For the rest of the files from that diabolo repository, "diabolo_motion_generator.h" is the header file for "diabolo_motion_generator.cpp" and "DiaboloSimConfig.msg" and "DiaboloState.msg" contain the structure for the messsage objects that pass data and store data in "diabolo_motion_generator.cpp".

My code:
The requirements.txt details the necessary libraries needed for the code in this directory.

"diabolo_motion_classes.py" contains the transplied DiaboloPredictor class with supporting classes.

"diabolo_motion_generator.py" contains the code that uses "diabolo_motion_classes.py" to run a prediction using von Drigalski et al.'s analytical model.

"output.csv" contains the output from running "diabolo_motion_generator.py". "correct_output.csv" contains the actual values from "circular_accel_stick_motion.csv", a data recording from von Drigalski et al.'s diabolo repository. "compare_results.py" computes the average distance between each point as an error metric.

"circular_accel_stick_motion_processed.csv" is "circular_accel_stick_motion.csv" but formatted to be more useful for analysis in python. "circular_accel_stick_motion_stick_poses.csv" is only the stick data from "circular_accel_stick_motion.csv".
