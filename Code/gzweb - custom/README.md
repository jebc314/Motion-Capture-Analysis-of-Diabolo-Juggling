Files modified and/or added:
- gzgui.js
- gzgui_revised.js
- gzspawnmodel.js
- index.html
- custom_embedded_scene.html
- files in the "models" folder
  - my_diabolo, stick_left, and stick_right are used in my final version
  - To use these models for gzweb/running the custom.world, you must tell the software where to locate them: export GAZEBO_MODEL_PATH=$HOME/gzweb/examples/models:$GAZEBO_MODEL_PATH. I had them in the examples folder in gzweb.
- custom.world is the world file I used when running gzserver for gzweb.
- jeb_site.html (old version of my website)

For using gzweb with my files, replace gzgui.js and gzspawnmodel.js with my versions.