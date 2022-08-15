My pitch prediction algorithm was developed in this directory.

The bulk of it is in the directory, 20220302Full-tilt, which utilizes my recording data file named "202203032Full-tilt.csv".

I also applied it to the data file "20220302Full 6-more tilt.csv". 

In the folder "20220302Full-tilt":

- The file "processing.ipynb" includes my testing of confirming the relation between pitch and offset angles.
- The file "smoothed_processing.ipynb" includes the addition of the savgol_filter to smooth my processing.
- The file "angular_speed.ipynb" includes my testing of determining angular speed from the roll angles. In the final pitch prediction - algorithm, the angular speed used is from von Drigalski et al.'s algorithm.
- The file "angular_speed_and_offset.ipynb" includes my testing of confirming the relation between pitch, offset angles, and angular speed and determining the value of k. There is also pitch prediction done using k and the offset and angular speed ratios.

The folder "20220302Full-tilt/data" includes all the different processing I did on the "202203032Full-tilt.csv" data file, including slicing to certain sections and isolating only the stick data.