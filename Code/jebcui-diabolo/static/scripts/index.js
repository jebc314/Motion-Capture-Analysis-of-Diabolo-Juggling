if (!Detector.webgl)
Detector.addGetWebGLMessage();

var scene, container, playDiv;

function start_button(value) {
    var values = value.split(" ");
    if (values[0] === 'Move') {
    scene.emitter.emit('custom_moves', 'move'+values[1]);
    console.log('move'+values[1]+' value for custom_moves listener');
    } else if (values[0] === 'Data') {
        var contents = $('#start-button').attr('Data');
        var processedData = $.csv.toObjects(contents);//processData(contents);
        console.log(processedData);
            
        //runFromData({'Wand':'stick_pos'}, processedData);
        runFromData({'Diabolo': 'my_diabolo','stick_right':'stick_right','stick_left':'stick_left'}, processedData);
    }
}

// Initialization
function init() {
    // Get URL
    var url = document.getElementById('url-input').value;

    // Clear URL input div
    var urlDiv = document.getElementById('url-div');
    while (urlDiv.firstChild) {
        urlDiv.removeChild(urlDiv.firstChild);
    }

    // Initialize objects
    var shaders = new GZ3D.Shaders();
    scene = new GZ3D.Scene(shaders);
    var iface = new GZ3D.GZIface(scene, url);
    var sdfparser = new GZ3D.SdfParser(scene, undefined, iface);

    // Listen to simulation events using the emitter
    scene.emitter.on('setPaused', serverPaused);

    // Configure scene
    scene.grid.visible = true;

    // Append to dom
    container = document.getElementById( 'container' );
    container.innerHTML = "";
    container.appendChild(scene.getDomElement());

    window.addEventListener('resize', onWindowResize, false);
    onWindowResize();

    // Add URL to page
    var urlHeader = document.createElement("h3");
    urlHeader.appendChild(document.createTextNode("Connected to " + url));
    urlDiv.appendChild(urlHeader);

    // This will hold a play/pause button according to info coming from the
    // server
    playDiv = document.createElement("div");
    urlDiv.appendChild(playDiv);

    
    scene.allModels = ['side_pos', 'side_neg', 'stick_pos', 'stick_neg', 'diabolo'];
    scene.currentIntervalId = null;

    // Download button
    $('#move_download').click(function(){
        const downloadToFile = (content, filename, contentType) => {
            const a = document.createElement('a');
            const file = new Blob([content], {type: contentType});
            
            a.href= URL.createObjectURL(file);
            a.download = filename;
            a.click();
            
            URL.revokeObjectURL(a.href);
            };

            downloadToFile($('#move_download').attr('move'), 'move_data.txt', 'text/plain');
    });

    // Upload button
    $('#move_upload').click(function(e){
        $('#fileInput').click();
    });

    $('#fileInput').change(function(){
        var file = this.files[0];
        console.log(file);
        // Saves file to static/files
        const formData = new FormData();
        formData.append('data', file);
        const xhr = new XMLHttpRequest();
        xhr.onload = () => {
            console.log(xhr.response);
            $('#run_simulation').attr('Data_location', xhr.response);
        };
        xhr.open("POST", "/savedata");
        xhr.send(formData);

        var reader = new FileReader();
        reader.onload = function(e) {
            var contents = e.target.result;
            $('#start-button').attr('value', 'Data Data');
            $('#start-button').attr('Data', contents);
            $('#move_download').attr('move', contents);
        };
        reader.readAsText(file);
    });

    $('#run_simulation').click(function(){
        const Http = new XMLHttpRequest();
       
        const url = '/predict?data_location=' + $('#run_simulation').attr('Data_location'); 
        Http.open("GET", url);
        Http.send();

        Http.onreadystatechange = (e) => {
            output = JSON.parse(Http.responseText);
            console.log(output);
            runFromData({'Diabolo': 'my_diabolo','stick_right':'stick_right','stick_left':'stick_left'}, output);
        }
    });

    // On custom_moves
    scene.emitter.on('custom_moves', processMove);  

    animate();
    
    // Set the camera in the right position and angle
    var camera = scene.camera;
    camera.position.x = 0;
    camera.position.y = -45;
    camera.position.z = 40;
    camera.quaternion.x = 0.383;
    camera.quaternion.y = 0;
    camera.quaternion.z = 0
    camera.quaternion.w = 0.924;
}

// Callback when window is resized
function onWindowResize() {
    scene.setSize(container.clientWidth, container.clientHeight);
}

// Recursively called animation loop
function animate() {
    requestAnimationFrame(animate);
    scene.render();
}

// Callback when server updates play/pause stats
function serverPaused(_paused) {
    if (_paused)
        setButtonPlay();
    else
        setButtonPause();
}

// Callback when user requests to play simulation
function userPlay() {
    // Send commands by using the emitter
    scene.emitter.emit('pause', false);
    setButtonPause();
}

// Callback when user requests to pause simulation
function userPause() {
    scene.emitter.emit('pause', true);
    setButtonPlay();
}

// Update the play/pause button so it says play
function setButtonPlay() {
    playDiv.innerHTML = "<button onclick='userPlay()'>Play!</button>";
}

// Update the play/pause button so it says pause
function setButtonPause() {
    playDiv.innerHTML = "<button onclick='userPause()'>Pause!</button>";
}

var intervalId = null;
var varCounter = null;
var varName = null;
function processMove(move) {
    $('#move_download').attr('move', move);
    if (scene.currentIntervalId !== null) {
        clearInterval(scene.currentIntervalId);
    }
    // Move all models away
    scene.allModels.forEach(function (item, index) {
        var model = scene.getByName(item);
        // Move 
        model.position.x = 100;
        model.position.y = 100;
        model.position.z = 100;
    });

    // what the move does
    if (move === 'move1'){
        console.log(move + ' value recieved by custom_moves listener');
        console.log(scene);

        $('#moves_description').text('These two long cylinders \nrepresent the sticks \nused in diabolo play.');

        // Move stick_pos
        var obj = scene.getByName('stick_pos');
        console.log(obj);
        obj.position.x = 6;
        obj.position.y = 0;
        obj.position.z = 15;

        // move stick_pos
        var obj = scene.getByName('stick_neg');
        console.log(obj);
        obj.position.x = -6;
        obj.position.y = 0;
        obj.position.z = 15;

        intervalId = null;
        varCounter = 0;
        varName = function(){
            if(varCounter <= 100) {
                varCounter++;

                var angle = varCounter/10 % 2 * Math.PI;
                // stick_pos movement
                var model = scene.getByName('stick_pos');
                model.position.x = 6 + 2*Math.cos(angle);
                model.position.y = 0;
                model.position.z = 15 + 2*Math.sin(angle);

                var roll = 1.57;
                var pitch = 0;
                var yaw = 0;

                rotate(model, roll, pitch, yaw);

                // stick_neg movement
                model = scene.getByName('stick_neg');
                model.position.x = -6 + 2*Math.cos(angle);
                model.position.y = 0;
                model.position.z = 15 + 2*Math.sin(angle);

                roll = 1.57;
                pitch = 0;
                yaw = 0;

                rotate(model, roll, pitch, yaw);

                // console.log('stick_neg_0 moved');
            } else {
                clearInterval(intervalId);
            }
        };
            
        intervalId = setInterval(varName, 100);
        scene.currentIntervalId = intervalId;
    }else if (move === 'move2') {
        console.log(move + ' value recieved by custom_moves listener');
        console.log(scene);

        $('#moves_description').text('This is a diabolo \nrotating around the z-axis.');

        // move diabolo
        var obj = scene.getByName('diabolo');
        console.log(obj);
        obj.position.x = 0;
        obj.position.y = 0;
        obj.position.z = 0;

        intervalId = null;
        varCounter = 0;
        varName = function(){
            if(varCounter <= 100) {
                varCounter++;

                var angle = varCounter/10 % (2 * Math.PI);
                // diabolo movement
                var model = scene.getByName('diabolo');

                var roll = 0;
                var pitch = 0;
                var yaw = angle;

                rotate(model, roll, pitch, yaw);
            } else {
                clearInterval(intervalId);
            }
        };
            
        intervalId = setInterval(varName, 100);
        scene.currentIntervalId = intervalId;
    } else if (move==='move3') {
        console.log(move + ' value recieved by custom_moves listener');
        console.log(scene);
        
        $('#moves_description').text('This is the combination \nof moves 1 and 2.');

        // move stick_pos
        var obj = scene.getByName('stick_pos');
        console.log(obj);
        obj.position.x = 6;
        obj.position.y = 0;
        obj.position.z = 15;
        
        // move stick_pos
        obj = scene.getByName('stick_neg');
        console.log(obj);
        obj.position.x = -6;
        obj.position.y = 0;
        obj.position.z = 15;
        
        // move diabolo
        obj = scene.getByName('diabolo');
        console.log(obj);
        obj.position.x = 0;
        obj.position.y = 0;
        obj.position.z = 0;
        
        intervalId = null;
        varCounter = 0;
        varName = function(){
            if(varCounter <= 100) {
                varCounter++;
        
                var angle = varCounter/10 % (2 * Math.PI);
                // stick_pos movement
                var model = scene.getByName('stick_pos');
                model.position.x = 6 + 2*Math.cos(angle);
                model.position.y = 0;
                model.position.z = 15 + 2*Math.sin(angle);
    
                var roll = 1.57;
                var pitch = 0;
                var yaw = 0;
    
                rotate(model, roll, pitch, yaw);
        
                // stick_neg movement
                model = scene.getByName('stick_neg');
                model.position.x = -6 + 2*Math.cos(angle);
                model.position.y = 0;
                model.position.z = 15 + 2*Math.sin(angle);
        
                roll = 1.57;
                pitch = 0;
                yaw = 0;
        
                rotate(model, roll, pitch, yaw);
        
                // diabolo movement
                model = scene.getByName('diabolo');
                roll = 0;
                pitch = 0;
                yaw = angle;
        
                rotate(model, roll, pitch, yaw);
            } else {
                clearInterval(intervalId);
            }
        };
            
        intervalId = setInterval(varName, 100);
        scene.currentIntervalId = intervalId;
    }
}

// Gets inputed raw data from a Vicon recording
function processData(data) {
    // Removes the title "Objects"
    var endOfLine = data.indexOf("\n");
    data = data.slice(endOfLine+1);
    // Removes the 100
    endOfLine = data.indexOf("\n");
    data = data.slice(endOfLine+1);

    // Get the next line of object names (Global Angle NAME:NAME)
    endOfLine = data.indexOf("\n");
    var names = data.slice(0, endOfLine).split(",").filter(function(value){return value});
    names = names.map(function(value){return value.slice(value.indexOf(":")+1)});
    data = data.slice(endOfLine+1);

    // Remove "Frame,Sub Frame..." line to replace with custom one
    endOfLine = data.indexOf("\n");
    data = data.slice(endOfLine+1);
    var newLine = "Frame,Sub Frame";
    var coordLabels = ["RX","RY","RZ","TX","TY","TZ"];
    for (let i = 0; i<names.length; i++) {
        newLine += "," + names[i]+"-";
        newLine += coordLabels.join("," + names[i]+"-");
    }
    // Remove the units line
    endOfLine = data.indexOf("\n");
    data = data.slice(endOfLine+1);
    // Add back the column names ("Frame,Sub Frame...") but with object names now
    data = newLine + "\n" + data;
    console.log(data)
    return $.csv.toObjects(data);
}

// Run a recording/data on the scene
// Data is preformatted to be a json object with position/rotation data for each model
// [{Frame:, Sub Frame:, NAME-RX:, NAME-RY:, NAME-RZ:, NAME-TX:, NAME-TY:, NAME-TZ:}]
// Each model in the data also has a corresponding model in the models list
// models: {object name in data json object: object name in scene}
function runFromData(models, model_data){
    console.log('Running from a dataset');
    //console.log(data);
    
    $('#moves_description').text('This is running a dataset');
    
    intervalId = null;
    varCounter = 0;
    varName = function(){
        if(varCounter < model_data.length) {
            $('#moves_description').text('Time point ' + varCounter);
            dataLine = model_data[varCounter];
            // Loop through each model
            for (var modelNames in models) {
                model = scene.getByName(models[modelNames]);
                
                // Position
                model.position.x = dataLine[modelNames+'-TX']/10;
                model.position.y = dataLine[modelNames+'-TY']/10;
                model.position.z = dataLine[modelNames+'-TZ']/10;

                console.log(model.position);

                // Rotation
                rotate(model, 
                    dataLine[modelNames+'-RX'], 
                    dataLine[modelNames+'-RY'], 
                    dataLine[modelNames+'-RZ']);
                // Rotation using quaternion
                /*
                rotateQuaternion(model, 
                    dataLine[modelNames+'-RX'], 
                    dataLine[modelNames+'-RY'], 
                    dataLine[modelNames+'-RZ'],
                    dataLine[modelNames+'-RW']);
                */
                console.log(model.quaternion, model.rotation);
            }

            varCounter++;
        } else {
            clearInterval(intervalId);
        }
    };
        
    intervalId = setInterval(varName, 1/600);
    scene.currentIntervalId = intervalId;
}

// Rotate based on roll, pitch, and yaw
function rotate(model, roll, pitch, yaw) {
    qx = Math.sin(roll/2) * Math.cos(pitch/2) * Math.cos(yaw/2) - Math.cos(roll/2) * Math.sin(pitch/2) * Math.sin(yaw/2);
    qy = Math.cos(roll/2) * Math.sin(pitch/2) * Math.cos(yaw/2) + Math.sin(roll/2) * Math.cos(pitch/2) * Math.sin(yaw/2);
    qz = Math.cos(roll/2) * Math.cos(pitch/2) * Math.sin(yaw/2) - Math.sin(roll/2) * Math.sin(pitch/2) * Math.cos(yaw/2);
    qw = Math.cos(roll/2) * Math.cos(pitch/2) * Math.cos(yaw/2) + Math.sin(roll/2) * Math.sin(pitch/2) * Math.sin(yaw/2);

    model.quaternion.w = qw;
    model.quaternion.x = qx;
    model.quaternion.y = qy;
    model.quaternion.z = qz;
}

// Rotate but without conversion to quaternion
function rotateEuler(model, roll, pitch, yaw) {
    model.rotation.x = roll;
    model.rotation.y = pitch;
    model.rotation.z = yaw;
}

// Rotate directly using quaternions
function rotateQuaternion(model, qx, qy, qz, qw) {
    model.quaternion.w = qw;
    model.quaternion.x = qx;
    model.quaternion.y = qy;
    model.quaternion.z = qz;
}