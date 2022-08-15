This directory contains my code that develops the R-PLNN model.

"preprocessing.ipynb" generates the files "output.csv", which contains the predicted position and angular velocity of the diabolo by the analytical model, "output_pitch.csv", which contains the predicted pitch values by the analytical model, and "calculated_angular_speed" which contains actual angular velocity for training.

"NN_training.ipynb" goes through the process of preparing training and testing data for my R-PLNN model. The model is saved to the directory "my_model_ll".