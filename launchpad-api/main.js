const Launchpad = require( 'launchpad-mini' ),
    readline = require('readline'),
    pad = new Launchpad(),
    rl = readline.createInterface({
        input: process.stdin
    })

pad.connect().then(() => {
    console.log(JSON.stringify({event: 'connected'}))
    pad.reset()
    pad.brightness(1)

    pad.on( 'key', ({x, y, pressed}) => {
        console.log(JSON.stringify({event: 'key', x, y, pressed}))
        // Make button red while pressed, green after pressing
        pad.col( pressed ? pad.red : pad.red.off, [x, y])
    })
})


rl.on('line', input => {
    const command = JSON.parse(input)
    if (command.event === 'col') {
        if (command.x < 0 || command.x > 8 || command.y < 0 || command.y > 8 || command.x + command.y >= 16) {
            console.log(JSON.stringify({event: 'invalid', command}))
            return
        }
        console.log(JSON.stringify({event: 'confirm', command}))
        pad.col(pad[command.color], [command.x, command.y])
    }
    if (command.event === 'reset') {
        console.log(JSON.stringify({event: 'confirm', command}))
        pad.reset()
    }
})

/*

// Fade from dark to bright ...
    (new Array( 100 )).fill( 0 ).forEach(
        // Set a bunch of timeouts which will change brightness
        ( empty, ix ) => setTimeout(
            () => pad.brightness( ix / 99 ), // ix ranges from 0 to 99
            ix * 20 // set new brightness every 20 ms
        )
    );

    pad.col(pad.red, [0,1])
    pad.col(pad.green, [0,2])
    pad.col(pad.yellow, [0,3])
    pad.col(pad.amber, [0,4])

    pad.col(pad.red.medium, [1,1])
    pad.col(pad.green.medium, [1,2])
    pad.col(pad.yellow.medium, [1,3])
    pad.col(pad.amber.medium, [1,4])

    pad.col(pad.red.full, [2,1])
    pad.col(pad.green.full, [2,2])
    pad.col(pad.yellow.full, [2,3])
    pad.col(pad.amber.full, [2,4])
 */
