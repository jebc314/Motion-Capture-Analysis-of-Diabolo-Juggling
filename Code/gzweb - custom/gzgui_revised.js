$(function()
{
    //Initialize
    // etc...

    // Custom Gui vvvv

    // Button for move 1 with id move1
    $('#move1').click(function(){
        // Emits value move1 for listener custom-moves
        globalEmitter.emit('custom_moves', 'move1');
        console.log('move1 value for custom_moves listener');
    });

    // Button for move 2 with id move2
    $('#move2').click(function(){
        // Emits value move1 for listener custom-moves
        globalEmitter.emit('custom_moves', 'move2');
        console.log('move2 value for custom_moves listener');
    });

    // Button for move 3 with id move3
    $('#move3').click(function(){
        // Emits value move1 for listener custom-moves
        globalEmitter.emit('custom_moves', 'move3');
        console.log('move3 value for custom_moves listener');
    });

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
});

/**
 * Graphical user interface
 * @constructor
 * @param {GZ3D.Scene} scene - A scene to connect to
 */
GZ3D.Gui = function(scene)
{
    this.emitter = globalEmitter || new EventEmitter2({verboseMemoryLeak: true});
    this.scene = scene;
    this.domElement = scene.getDomElement();
    this.spawnState = null;
    this.longPressContainerState = null;
    this.showNotifications = false;
    this.openTreeWhenSelected = false;
    this.modelStatsDirty = false;

    this.logPlay = new GZ3D.LogPlay();

    this.currentModels = [];
    this.currentIntervalId = null;

    var that = this;

    // etc...

    // On custom_moves
    this.emitter.on('custom_moves',
        function(move) {
            $('#move_download').attr('move', move);
            if (that.currentIntervalId !== null) {
                clearInterval(that.currentIntervalId);
            }
            // Delete current models
            that.currentModels.forEach(function (item, index) {
                that.scene.selectEntity(that.scene.getByName(item));
                globalEmitter.emit('delete_entity');
            });
            that.currentModels = [];

            // what the move does
            var entity1 = null;
            var name1 = null;
            var entity2 = null;
            var name2 = null;
            var entity3 = null;
            var name3 = null;
            var entity4 = null;
            var name4 = null;
            var intervalId = null;
            var varCounter = null;
            var varName = null;
            if (move === 'move1') {
                console.log(move + ' value recieved by custom_moves listener');
                console.log(that.scene);

                $('#moves_description').text('These two long cylinders \nrepresent the sticks \nused in diabolo play.');

                // spawn stick_pos
                entity1 = 'stick_pos';
                name1 = getNameFromPath(entity1);
                that.spawnState = 'START';
                that.scene.spawnModel.place(entity1,function(obj)
                    {
                        that.emitter.emit('entityCreated', obj, entity1);
                        console.log(obj);
                        that.scene.getByName('stick_pos_0').position.x = 6;
                        that.scene.getByName('stick_pos_0').position.y = 0;
                        that.scene.getByName('stick_pos_0').position.z = 15;
                        that.currentModels.push('stick_pos_0');
                    });

                that.emitter.emit('notification_popup', 'Place '+name1);

                // spawn stick_pos
                entity2 = 'stick_neg';
                name2 = getNameFromPath(entity2);
                that.spawnState = 'START';
                that.scene.spawnModel.place(entity2,function(obj)
                    {
                        that.emitter.emit('entityCreated', obj, entity2);
                        console.log(obj);
                        that.scene.getByName('stick_neg_0').position.x = -6;
                        that.scene.getByName('stick_neg_0').position.y = 0;
                        that.scene.getByName('stick_neg_0').position.z = 15;
                        that.currentModels.push('stick_neg_0');
                    });

                that.emitter.emit('notification_popup', 'Place '+name2);

                intervalId = null;
                varCounter = 0;
                varName = function(){
                    if(varCounter <= 100) {
                        varCounter++;

                        var angle = varCounter/10 % 2 * Math.PI;
                            // stick_pos movement
                            var model = that.scene.getByName('stick_pos_0');
                            model.position.x = 6 + 2*Math.cos(angle);
                            model.position.y = 0;
                            model.position.z = 15 + 2*Math.sin(angle);

                            var roll = 1.57;
                            var pitch = 0;
                            var yaw = 0;

                            var qx = Math.sin(roll/2) * Math.cos(pitch/2) * Math.cos(yaw/2) - Math.cos(roll/2) * Math.sin(pitch/2) * Math.sin(yaw/2);
                            var qy = Math.cos(roll/2) * Math.sin(pitch/2) * Math.cos(yaw/2) + Math.sin(roll/2) * Math.cos(pitch/2) * Math.sin(yaw/2);
                            var qz = Math.cos(roll/2) * Math.cos(pitch/2) * Math.sin(yaw/2) - Math.sin(roll/2) * Math.sin(pitch/2) * Math.cos(yaw/2);
                            var qw = Math.cos(roll/2) * Math.cos(pitch/2) * Math.cos(yaw/2) + Math.sin(roll/2) * Math.sin(pitch/2) * Math.sin(yaw/2);

                            model.quaternion.w = qw;
                            model.quaternion.x = qx;
                            model.quaternion.y = qy;
                            model.quaternion.z = qz;

                        // console.log('stick_pos_0 moved');

                        // stick_neg movement
                        model = that.scene.getByName('stick_neg_0');
                        model.position.x = -6 + 2*Math.cos(angle);
                        model.position.y = 0;
                        model.position.z = 15 + 2*Math.sin(angle);

                        roll = 1.57;
                        pitch = 0;
                        yaw = 0;

                        qx = Math.sin(roll/2) * Math.cos(pitch/2) * Math.cos(yaw/2) - Math.cos(roll/2) * Math.sin(pitch/2) * Math.sin(yaw/2);
                        qy = Math.cos(roll/2) * Math.sin(pitch/2) * Math.cos(yaw/2) + Math.sin(roll/2) * Math.cos(pitch/2) * Math.sin(yaw/2);
                        qz = Math.cos(roll/2) * Math.cos(pitch/2) * Math.sin(yaw/2) - Math.sin(roll/2) * Math.sin(pitch/2) * Math.cos(yaw/2);
                        qw = Math.cos(roll/2) * Math.cos(pitch/2) * Math.cos(yaw/2) + Math.sin(roll/2) * Math.sin(pitch/2) * Math.sin(yaw/2);

                        model.quaternion.w = qw;
                        model.quaternion.x = qx;
                        model.quaternion.y = qy;
                        model.quaternion.z = qz;

                        // console.log('stick_neg_0 moved');
                    } else {
                        clearInterval(intervalId);
                        //that.scene.selectEntity(that.scene.getByName('stick_pos_0'));
                        //globalEmitter.emit('delete_entity');
                        //that.scene.selectEntity(that.scene.getByName('stick_neg_0'));
                        //globalEmitter.emit('delete_entity');
                        console.log(that.currentModels);
                    }
                };
                    
                intervalId = setInterval(varName, 100);
                that.currentIntervalId = intervalId;
            } else if (move === 'move2') {
                console.log(move + ' value recieved by custom_moves listener');
                console.log(that.scene);

                $('#moves_description').text('These two disks represent \nthe sides of a diabolo \nrotating around the z-axis.');

                // spawn side_pos
                entity1 = 'side_pos';
                name1 = getNameFromPath(entity1);
                that.spawnState = 'START';
                that.scene.spawnModel.place(entity1,function(obj)
                    {
                        that.emitter.emit('entityCreated', obj, entity1);
                        console.log(obj);
                        that.scene.getByName('side_pos_0').position.x = 0;
                        that.scene.getByName('side_pos_0').position.y = 0;
                        that.scene.getByName('side_pos_0').position.z = 7;
                        that.currentModels.push('side_pos_0');
                    });

                that.emitter.emit('notification_popup', 'Place '+name1);

                // spawn side_pos
                entity2 = 'side_neg';
                name2 = getNameFromPath(entity2);
                that.spawnState = 'START';
                that.scene.spawnModel.place(entity2,function(obj)
                    {
                        that.emitter.emit('entityCreated', obj, entity2);
                        console.log(obj);
                        that.scene.getByName('side_neg_0').position.x = 0;
                        that.scene.getByName('side_neg_0').position.y = 0;
                        that.scene.getByName('side_neg_0').position.z = 7;
                        that.currentModels.push('side_neg_0');
                    });

                that.emitter.emit('notification_popup', 'Place '+name2);

                intervalId = null;
                varCounter = 0;
                varName = function(){
                    if(varCounter <= 100) {
                        varCounter++;

                        var angle = varCounter/10 % (2 * Math.PI);
                            // side_pos movement
                            var model = that.scene.getByName('side_pos_0');
                            model.position.x = 4*Math.cos(angle);
                            model.position.y = 4*Math.sin(angle);
                            model.position.z = 7;

                            var roll = 0;
                            var pitch = 1.57;
                            var yaw = angle;

                            var qx = Math.sin(roll/2) * Math.cos(pitch/2) * Math.cos(yaw/2) - Math.cos(roll/2) * Math.sin(pitch/2) * Math.sin(yaw/2);
                            var qy = Math.cos(roll/2) * Math.sin(pitch/2) * Math.cos(yaw/2) + Math.sin(roll/2) * Math.cos(pitch/2) * Math.sin(yaw/2);
                            var qz = Math.cos(roll/2) * Math.cos(pitch/2) * Math.sin(yaw/2) - Math.sin(roll/2) * Math.sin(pitch/2) * Math.cos(yaw/2);
                            var qw = Math.cos(roll/2) * Math.cos(pitch/2) * Math.cos(yaw/2) + Math.sin(roll/2) * Math.sin(pitch/2) * Math.sin(yaw/2);

                            model.quaternion.w = qw;
                            model.quaternion.x = qx;
                            model.quaternion.y = qy;
                            model.quaternion.z = qz;

                        // console.log('stick_pos_0 moved');

                        // side_neg movement
                        // console.log(angle);
                        angle = (varCounter/10 + Math.PI) % (2 * Math.PI);
                        // console.log(angle);
                        model = that.scene.getByName('side_neg_0');
                        model.position.x = 4*Math.cos(angle);
                        model.position.y = 4*Math.sin(angle);
                        model.position.z = 7;

                        roll = 0;
                        pitch = 1.57;
                        yaw = angle;

                        qx = Math.sin(roll/2) * Math.cos(pitch/2) * Math.cos(yaw/2) - Math.cos(roll/2) * Math.sin(pitch/2) * Math.sin(yaw/2);
                        qy = Math.cos(roll/2) * Math.sin(pitch/2) * Math.cos(yaw/2) + Math.sin(roll/2) * Math.cos(pitch/2) * Math.sin(yaw/2);
                        qz = Math.cos(roll/2) * Math.cos(pitch/2) * Math.sin(yaw/2) - Math.sin(roll/2) * Math.sin(pitch/2) * Math.cos(yaw/2);
                        qw = Math.cos(roll/2) * Math.cos(pitch/2) * Math.cos(yaw/2) + Math.sin(roll/2) * Math.sin(pitch/2) * Math.sin(yaw/2);

                        model.quaternion.w = qw;
                        model.quaternion.x = qx;
                        model.quaternion.y = qy;
                        model.quaternion.z = qz;

                        // console.log('stick_neg_0 moved');
                    } else {
                        clearInterval(intervalId);
                        //that.scene.selectEntity(that.scene.getByName('stick_pos_0'));
                        //globalEmitter.emit('delete_entity');
                        //that.scene.selectEntity(that.scene.getByName('stick_neg_0'));
                        //globalEmitter.emit('delete_entity');
                        console.log(that.currentModels);
                    }
                };
                    
                intervalId = setInterval(varName, 100);
                that.currentIntervalId = intervalId;
            } else if (move==='move3') {
                console.log(move + ' value recieved by custom_moves listener');
                console.log(that.scene);
                
                $('#moves_description').text('This is the combination \nof moves 1 and 2.');

                // spawn stick_pos
                entity1 = 'stick_pos';
                name1 = getNameFromPath(entity1);
                that.spawnState = 'START';
                that.scene.spawnModel.place(entity1,function(obj)
                    {
                        that.emitter.emit('entityCreated', obj, entity1);
                        console.log(obj);
                        that.scene.getByName('stick_pos_0').position.x = 6;
                        that.scene.getByName('stick_pos_0').position.y = 0;
                        that.scene.getByName('stick_pos_0').position.z = 15;
                        that.currentModels.push('stick_pos_0');
                    });
                
                that.emitter.emit('notification_popup', 'Place '+name1);
                
                // spawn stick_pos
                entity2 = 'stick_neg';
                name2 = getNameFromPath(entity2);
                that.spawnState = 'START';
                that.scene.spawnModel.place(entity2,function(obj)
                    {
                        that.emitter.emit('entityCreated', obj, entity2);
                        console.log(obj);
                        that.scene.getByName('stick_neg_0').position.x = -6;
                        that.scene.getByName('stick_neg_0').position.y = 0;
                        that.scene.getByName('stick_neg_0').position.z = 15;
                        that.currentModels.push('stick_neg_0');
                    });
                
                that.emitter.emit('notification_popup', 'Place '+name2);
                
                // spawn side_pos
                entity3 = 'side_pos';
                name3 = getNameFromPath(entity3);
                that.spawnState = 'START';
                that.scene.spawnModel.place(entity3,function(obj)
                    {
                        that.emitter.emit('entityCreated', obj, entity3);
                        console.log(obj);
                        that.scene.getByName('side_pos_1').position.x = 0;
                        that.scene.getByName('side_pos_1').position.y = 0;
                        that.scene.getByName('side_pos_1').position.z = 7;
                        that.currentModels.push('side_pos_1');
                    });
                
                that.emitter.emit('notification_popup', 'Place '+name3);
                
                // spawn side_pos
                entity4 = 'side_neg';
                name4 = getNameFromPath(entity4);
                that.spawnState = 'START';
                that.scene.spawnModel.place(entity4,function(obj)
                    {
                        that.emitter.emit('entityCreated', obj, entity4);
                        console.log(obj);
                        that.scene.getByName('side_neg_1').position.x = 0;
                        that.scene.getByName('side_neg_1').position.y = 0;
                        that.scene.getByName('side_neg_1').position.z = 7;
                        that.currentModels.push('side_neg_1');
                    });
                
                that.emitter.emit('notification_popup', 'Place '+name4);
                
                intervalId = null;
                varCounter = 0;
                varName = function(){
                    if(varCounter <= 100) {
                        varCounter++;
                
                        var angle = varCounter/10 % (2 * Math.PI);
                            // stick_pos movement
                            var model = that.scene.getByName('stick_pos_0');
                            model.position.x = 6 + 2*Math.cos(angle);
                            model.position.y = 0;
                            model.position.z = 15 + 2*Math.sin(angle);
                
                            var roll = 1.57;
                            var pitch = 0;
                            var yaw = 0;
                
                            var qx = Math.sin(roll/2) * Math.cos(pitch/2) * Math.cos(yaw/2) - Math.cos(roll/2) * Math.sin(pitch/2) * Math.sin(yaw/2);
                            var qy = Math.cos(roll/2) * Math.sin(pitch/2) * Math.cos(yaw/2) + Math.sin(roll/2) * Math.cos(pitch/2) * Math.sin(yaw/2);
                            var qz = Math.cos(roll/2) * Math.cos(pitch/2) * Math.sin(yaw/2) - Math.sin(roll/2) * Math.sin(pitch/2) * Math.cos(yaw/2);
                            var qw = Math.cos(roll/2) * Math.cos(pitch/2) * Math.cos(yaw/2) + Math.sin(roll/2) * Math.sin(pitch/2) * Math.sin(yaw/2);
                
                            model.quaternion.w = qw;
                            model.quaternion.x = qx;
                            model.quaternion.y = qy;
                            model.quaternion.z = qz;
                
                        // console.log('stick_pos_0 moved');
                
                        // stick_neg movement
                        model = that.scene.getByName('stick_neg_0');
                        model.position.x = -6 + 2*Math.cos(angle);
                        model.position.y = 0;
                        model.position.z = 15 + 2*Math.sin(angle);
                
                        roll = 1.57;
                        pitch = 0;
                        yaw = 0;
                
                        qx = Math.sin(roll/2) * Math.cos(pitch/2) * Math.cos(yaw/2) - Math.cos(roll/2) * Math.sin(pitch/2) * Math.sin(yaw/2);
                        qy = Math.cos(roll/2) * Math.sin(pitch/2) * Math.cos(yaw/2) + Math.sin(roll/2) * Math.cos(pitch/2) * Math.sin(yaw/2);
                        qz = Math.cos(roll/2) * Math.cos(pitch/2) * Math.sin(yaw/2) - Math.sin(roll/2) * Math.sin(pitch/2) * Math.cos(yaw/2);
                        qw = Math.cos(roll/2) * Math.cos(pitch/2) * Math.cos(yaw/2) + Math.sin(roll/2) * Math.sin(pitch/2) * Math.sin(yaw/2);
                
                        model.quaternion.w = qw;
                        model.quaternion.x = qx;
                        model.quaternion.y = qy;
                        model.quaternion.z = qz;
                
                        // console.log('stick_neg_0 moved');
                        // side_pos movement
                        model = that.scene.getByName('side_pos_1');
                        model.position.x = 4*Math.cos(angle);
                        model.position.y = 4*Math.sin(angle);
                        model.position.z = 7;
                
                        roll = 0;
                        pitch = 1.57;
                        yaw = angle;
                
                        qx = Math.sin(roll/2) * Math.cos(pitch/2) * Math.cos(yaw/2) - Math.cos(roll/2) * Math.sin(pitch/2) * Math.sin(yaw/2);
                        qy = Math.cos(roll/2) * Math.sin(pitch/2) * Math.cos(yaw/2) + Math.sin(roll/2) * Math.cos(pitch/2) * Math.sin(yaw/2);
                        qz = Math.cos(roll/2) * Math.cos(pitch/2) * Math.sin(yaw/2) - Math.sin(roll/2) * Math.sin(pitch/2) * Math.cos(yaw/2);
                        qw = Math.cos(roll/2) * Math.cos(pitch/2) * Math.cos(yaw/2) + Math.sin(roll/2) * Math.sin(pitch/2) * Math.sin(yaw/2);
                
                        model.quaternion.w = qw;
                        model.quaternion.x = qx;
                        model.quaternion.y = qy;
                        model.quaternion.z = qz;
                
                        // console.log('stick_pos_0 moved');
                
                        // side_neg movement
                        // console.log(angle);
                        angle = (varCounter/10 + Math.PI) % (2 * Math.PI);
                        // console.log(angle);
                        model = that.scene.getByName('side_neg_1');
                        model.position.x = 4*Math.cos(angle);
                        model.position.y = 4*Math.sin(angle);
                        model.position.z = 7;
                
                        roll = 0;
                        pitch = 1.57;
                        yaw = angle;
                
                        qx = Math.sin(roll/2) * Math.cos(pitch/2) * Math.cos(yaw/2) - Math.cos(roll/2) * Math.sin(pitch/2) * Math.sin(yaw/2);
                        qy = Math.cos(roll/2) * Math.sin(pitch/2) * Math.cos(yaw/2) + Math.sin(roll/2) * Math.cos(pitch/2) * Math.sin(yaw/2);
                        qz = Math.cos(roll/2) * Math.cos(pitch/2) * Math.sin(yaw/2) - Math.sin(roll/2) * Math.sin(pitch/2) * Math.cos(yaw/2);
                        qw = Math.cos(roll/2) * Math.cos(pitch/2) * Math.cos(yaw/2) + Math.sin(roll/2) * Math.sin(pitch/2) * Math.sin(yaw/2);
                
                        model.quaternion.w = qw;
                        model.quaternion.x = qx;
                        model.quaternion.y = qy;
                        model.quaternion.z = qz;
                
                        // console.log('stick_neg_0 moved');
                    } else {
                        clearInterval(intervalId);
                        //that.scene.selectEntity(that.scene.getByName('stick_pos_0'));
                        //globalEmitter.emit('delete_entity');
                        //that.scene.selectEntity(that.scene.getByName('stick_neg_0'));
                        //globalEmitter.emit('delete_entity');
                        console.log(that.currentModels);
                    }
                };
                    
                intervalId = setInterval(varName, 100);
                that.currentIntervalId = intervalId;
            }
        }
    );  
}