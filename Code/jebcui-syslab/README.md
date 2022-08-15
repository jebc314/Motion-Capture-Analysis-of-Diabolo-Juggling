# jebcui-syslab
Jeb Cui's Sys Lab Project

This doesn't include the analytical/R-PLNN model in the site itself. Refer to jebcui-diabolo for that.

# What's not included | How to get them

- Vicon DataStream SDK | 
	Go through the process of the installer, go to the program location, find the python folder, copy the folder vicon_dssdk to this directory, and then with your python virtual environment activated, run pip install "vicon_dssdk".
- Virtual environment | create a virtual environment as you would for other flask applications, and use the "requirements.txt" file to help install dependencies. Installing the Vicon DataStream SDK should happen before this step to ensure compatibility.