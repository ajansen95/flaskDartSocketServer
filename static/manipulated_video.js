document.addEventListener("DOMContentLoaded", () => {
    const FPS = 62.5 // => ( 62.5; 50; 40; 32; 31.25; 25; 20; 16 )
    const TBF = 1000/FPS //=> TBF = Time Between Frames

    const socket = io.connect(`ws://${document.domain}:${location.port}/manipulated-camera-feed`);
    socket.on('manipulated-new-frame', message => {
        document.getElementById('manipulated-camera-frame').setAttribute(
            'src', `data:image/jpeg;base64,${message.base64}`
        );
    });
    window.setInterval(() => {
        socket.emit('request-manipulated-frame', {});
    }, TBF);
});