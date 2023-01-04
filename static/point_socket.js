document.addEventListener("DOMContentLoaded", () => {
    //console.log("Dom loaded")

    const socket = io.connect(`ws://${document.domain}:${location.port}/current-point-feed`);
    socket.on('current-point', message => {
        //console.log("Message:" + message)
        //console.log("Message.current-point:" + message.point)
        document.getElementById('points').innerHTML = `${message.point}`;
    });
    socket.emit('request-current-point', {})

});