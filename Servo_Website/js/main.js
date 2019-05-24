// SocketIO functions when the document is ready
$(document).ready(function(){

    // data that we'll be assigning and sending
    vec = Object.seal({
    shoulder: 0,
    elbow: 0
    });

    // Read and send the Dpad button states over MQTT

    var sending = false;
    var sending2 = false;
    var receiving = false;
    var subscribed = false;
    var connected = false;

    // Set up the MQTT client ** you have several options just uncomment to use **
    // iot.eclipse.org is default
    //server = "test.mosquitto.org"
    //port = 8080
    server = "iot.eclipse.org"
    // port = 1883
    //server = "broker.mqttdashboard.com"
    port = 80

    client = new Messaging.Client(server, port, "CRAWLAB_" + parseInt(Math.random() * 100, 10));


    // Select the MQTT server to use
    $("#server" ).on('change', function() {
        $('.receiving').toggleClass('on', false);
        if (connected) {
            client.disconnect();
            sending = false;
            receiving = false;
            subscribed = false;
            $('.connected').toggleClass('on', false);
            $('.sending').toggleClass('on', false);
            $('.subscribed').toggleClass('on', false);
            $('.receiving').toggleClass('on', false);
            $('#receive').text('Receive');
            $('#control').text('Start');
            $('#control2').text('OpenCV On');
            $('.sending2').toggleClass('on', false);

        }
        server = $(this).val();
        select = document.getElementById('#server');
        console.log(server);

        if (server == "iot.eclipse.org") {
            port = 80;
        }
        else if (server == "test.mosquitto.org") {
            port = 8080;
        }
        else if (server == "broker.mqtt-dashboard.com") {
            port = 8000;
        }
        client = new Messaging.Client(server, port, "CRAWLAB_" + parseInt(Math.random() * 100, 10));
        client.connect(options)

        //Gets  called if the websocket/mqtt connection gets disconnected for any reason
        client.onConnectionLost = function (responseObject) {
        //Depending on your scenario you could implement a reconnect logic here
        //alert("Connection Lost: " + responseObject.errorMessage);
        $('.connected').toggleClass('on');
        connected = false;
        };

        //Gets called whenever you receive a message for your subscriptions
        client.onMessageArrived = function (message) {
        //Do something with the push message you received
        if (receiving) {
        $('#messages').prepend('<span>Topic: ' + message.destinationName + '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Data: ' + message.payloadString + '</span><br/>');
        }
        };
    });

    //Connect Options
    options = {
         timeout: 3,
         //Gets Called if the connection has sucessfully been established
         onSuccess: function () {
//              alert("Connected");
            $('.connected').toggleClass('on');
            connected = true;
         },
         //Gets Called if the connection could not be established
         onFailure: function (message) {
             alert("Connection failed: " + message.errorMessage);
             $('.connected').toggleClass('on', false);
             connected = false;
         }
     };

    client.connect(options);

            //Gets  called if the websocket/mqtt connection gets disconnected for any reason
    client.onConnectionLost = function (responseObject) {
        //Depending on your scenario you could implement a reconnect logic here
        //alert("Connection Lost: " + responseObject.errorMessage);
        $('.connected').toggleClass('on');
        connected = false;
    };

    //Gets called whenever you receive a message for your subscriptions
    client.onMessageArrived = function (message) {
        //Do something with the push message you received
        if (receiving) {
        $('#messages').prepend('<span>Topic: ' + message.destinationName + '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Data: ' + message.payloadString + '</span><br/>');
        }
    };


    //Creates a new Messaging.Message Object and sends it to the HiveMQ MQTT Broker
    publish = function (payload, topic, qos) {
        //Send your message (also possible to serialize it as JSON or protobuf or just use a string, no limitations)
        var message = new Messaging.Message(payload);
        message.destinationName = topic;
        message.qos = qos;
        client.send(message);
    }




// Send the data over a MQTT 10 times per second (100ms)
toggle_sending = function () {
    if (sending) {
        webcam_off();
        if (timer) {
         clearTimeout(timer);
         timer = 0;
         $('#control').text('Start');
         sending = false;
        $('.sending').toggleClass('on');
        }
    }
    else {
        $("#control").text('Stop');
        $(".send_status").css("background-color","red");
        sending = true;
        webcam_on();
        //Send your message (also possible to serialize it as JSON or protobuf or just use a string, no limitations)
        send_data();
        $('.sending').toggleClass('on');
        };
    }
//////////////////////////////////////////////////////////////////
// Send the data over MQTT once
toggle_sending2 = function () {
    if (sending2) {
        //if (timer) {
         //clearTimeout(timer);
         //timer = 0;
        $('#control2').text('Opencv On');
        sending2 = false;
        $('.sending2').toggleClass('on');
        send_data_off();
        email_prompt();
        disable();
        //}
    }
    else {
        $("#control2").text('Stop');
        $(".send_status2").css("background-color","red");
        sending2 = true;
        //Send your message (also possible to serialize it as JSON or protobuf or just use a string, no limitations)
        send_data_on();
        $('.sending2').toggleClass('on');
        disable();
        };
    }
///////////////////////////////////////////////////////////////////

// Accept the data being sent
toggle_receiving = function () {
    if (receiving) {
         $('#receive').text('Receive');
         receiving = false;
        $('.receiving').toggleClass('on');
    }
    else
    {
        if (subscribed) {
            $("#receive").text('Stop');
            receiving = true;
            $('.receiving').toggleClass('on');
            $('#messages').text('');
            }
        else {
            alert("You must be subscribed to a topic to receive data published to it. Please subscribe and try again.")
        }

    }
    };

// Toggle susbscription
toggle_subscription = function () {
    if (subscribed) {
        $('.subscribed').toggleClass('on');
        client.unsubscribe('CRAWLAB/twoLink');
        subscribed = false;
    }
    else {
        $('.subscribed').toggleClass('on');
        client.subscribe('CRAWLAB/twoLink', {qos: 0});
        subscribed = true;
    }
    };


// Read the slider value when it changes
// From: http://stackoverflow.com/questions/17482636/html-range-slider-and-jquery
$('#small').on('change', function(){
   vec.elbow = document.querySelector('#small').value;
});

$('#big').on('change', function(){
   vec.shoulder = document.querySelector('#big').value
});


send_data = function (){
//Send your message (also possible to serialize it as JSON or protobuf or just use a string, no limitations)
         var message = new Messaging.Message(String(vec.shoulder) + ',' + String(vec.elbow));
         console.log('Sending on ' + 'CRAWLAB/twoLink: ' + String(vec.shoulder) + ',' + String(vec.elbow))
         message.destinationName = 'CRAWLAB/twoLink';
         message.qos = 0;
         client.send(message);
        timer = setTimeout(send_data, 50);
        }



//////////////////////////////////////////////////////////////////
send_data_on = function (){
//Send your message (also possible to serialize it as JSON or protobuf or just use a string, no limitations)
         var message2 = new Messaging.Message(String('on'));
         console.log('Sending on ' + 'CRAWLAB/twoLink/opencv: ' + String('on'))
         message2.destinationName = 'CRAWLAB/twoLink/opencv';
         message2.qos = 0;
         client.send(message2);
        //timer = setTimeout(send_data_on, 50);
        }

//////////////////////////////////////////////////////////////////
send_data_off = function (){
//Send your message (also possible to serialize it as JSON or protobuf or just use a string, no limitations)
         var message2 = new Messaging.Message(String('off'));
         console.log('Sending on ' + 'CRAWLAB/twoLink/opencv: ' + String('off'))
         message2.destinationName = 'CRAWLAB/twoLink/opencv';
         message2.qos = 0;
         client.send(message2);
        //timer = setTimeout(send_data_on, 50);
        }

//////////////////////////////////////////////////////////////////
email_prompt = function (){
  //After clicking the OpenCV button to stop this will ask for your email.
        var email = prompt("Please enter your email", "We won't spam you!");
        var email_mess = new Messaging.Message(email);
        console.log('Sending on ' + 'CRAWLAB/twoLink/opencv/email: ' + email);
        email_mess.destinationName = 'CRAWLAB/twoLink/opencv/email';
        email_mess.qos = 0;
        client.send(email_mess);
        }

//////////////////////////////////////////////////////////////////
webcam_on = function (){
  //After clicking the Start Button this will trigger a python scipt that will turn on the webcam.
        var Webcam_on = new Messaging.Message(String('on'));
        console.log('Sending on ' + 'CRAWLAB/twoLink/webcam: ' + String('on'))
        Webcam_on.destinationName = 'CRAWLAB/twoLink/webcam';
        Webcam_on.qos = 0;
        client.send(Webcam_on);
        //timer = setTimeout(send_data_on, 50);
        }
//////////////////////////////////////////////////////////////////
webcam_off = function (){
  //After clicking the Start Button this will trigger a python scipt that will turn off the webcam.
        var Webcam_off = new Messaging.Message(String('off'));
        console.log('Sending on ' + 'CRAWLAB/twoLink/webcam: ' + String('off'))
        Webcam_off.destinationName = 'CRAWLAB/twoLink/webcam';
        Webcam_off.qos = 0;
        client.send(Webcam_off);
        //timer = setTimeout(send_data_on, 50);
        }
//////////////////////////////////////////////////////////////////
disable = function (){
  // This script disables the OpenCV button so people don't click it too much.
  x = document.getElementById("control2");
  x.disabled = true;
  x.value = "Analyzing";
  setTimeout(enable, 3000);
}

function enable() {
  x.disabled = false;
  x.value = " Sending ";
}
});
