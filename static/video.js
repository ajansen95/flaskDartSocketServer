document.addEventListener("DOMContentLoaded", () => {
    const FPS = 16 // => ( 62.5; 50; 40; 32; 31.25; 25; 20; 16 )
    const TBF = 1000/FPS //=> TBF = Time Between Frames

    const socket = io.connect(`ws://${document.domain}:${location.port}/camera-feed`);
    socket.on('new-frame', message => {
        document.getElementById('camera-frame').setAttribute(
            'src', `data:image/jpeg;base64,${message.base64}`
        );
    });
    window.setInterval(() => {
        socket.emit('request-frame', {});
    }, TBF);
});