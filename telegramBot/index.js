//dependencies
const { Telegraf } = require('telegraf');
const { exec } = require('child_process');
const http = require('./app');
const os = require('os');
const fs = require('fs');
const open = require('open');

//check if it is a raspberry or just simulation
const isRaspberry = process.arch === 'arm';
const Gpio = isRaspberry ? require('onoff').Gpio : require('pigpio-mock').Gpio;

//load .env values
const dotenv = require('dotenv');
dotenv.config();

//bot initialization
const bot = new Telegraf(process.env.TOKEN);

//constants

const messageToSend =
`Soy xD Bot, el asistente virtual de xD Ring  😁😁
Formo parte de un sistema integrado desarrollado por Richard Arostegui y Mateo García, espero poder ayudarte, puedes:
1) Consultar fotos desde tu timbre 📷
2) Consultar las personas en mi base de Datos 📈
3) Escuchar un audio de prueba 🎤
4) Grabar un video 📸
5) Grabar un video con Reconocimiento Facial 📸👨
6) Apagar xD Ring y xD Bot
7) Ver vista del timbre en vivo
8) Añadir una nueva persona al reconocimiento facial
9) Abrir la Puerta`;
const chatId = process.env.CHAT_ID;
let button = new Gpio(17, 'in')
let led = new Gpio(27, 'out');
let door = new Gpio(22,'out');
let confirm = false;
let serverisWorking = false;
let isOk = false;
let personas = `Las personas que encontré en mi base de Datos fueron: `;
let peopleToSend = [];


//methods
const shutdownServer = (contextXd) => {
    serverisWorking = false;
    const tasks = exec('pgrep chromium-browser | cat > clientTask.txt && head -n 1 clientTask.txt' );

        tasks.stdout.on('data', (data) => {
            console.log(data);

            const killClient = exec(`kill ${data}`);

            killClient.stdout.on('data', (data) => {
                console.log(data);
            });
            killClient.stdout.on('error', (err) => {
                console.error(err)
            }) 
            killClient.on('exit', (code) => {
                console.log(`exit with code : ${code}`);
            });
        });
        tasks.stdout.on('error', (err) => {
            console.error(err)
        }) 
        tasks.on('exit', (code) => {
            console.log(`exit with code : ${code}`);

        });
        http.close();
        contextXd.reply('La transmisión en vivo se apagó correctamente');
}


const deleteFonderAudio = () => {
    fs.readdir('./telegramBot/audio', (err, files) => {
        let filesToDelete = 'sudo rm ';
        console.log(files);
        if(err){
            console.error(err);
            return;
        }
        if(files.length > 0){
            for(let i = 0; i < files.length; i++){
                filesToDelete += './telegramBot/audio/' + files[i] + ' ';
            }
            console.log(filesToDelete)
            const deleteFiles = exec(filesToDelete);

            //FUNCTION
            deleteFiles.stdout.on('data', (data) => {
                console.log(data);
            });
            deleteFiles.stdout.on('error', (err) => {
                console.error(err)
            });
            deleteFiles.on('exit', (code) => {
                console.log(`exit with code : ${code}`);
            });
        }
    });
}

deleteFonderAudio();

bot.start((ctx) => {
    ctx.reply('xD Ring y xD Bot están activos');
    console.log(ctx.chat.id);
    peopleToSend.push(ctx.chat.id);
});

//commands

bot.command('estado', (ctx) => {
    ctx.reply('funcionando');
});

bot.command('apagar', (ctx) => {
    ctx.reply(`Apagando xd Ring, hasta la próximaaaa 😎,
    Recuerda aplastar el botón de alimentación para apagar el timbre por completo, y cuando quieras encenderlo, simplemento aplasta el botón`)
    callOpenCv(6,ctx);
});


bot.command('ip',(ctx)=> {
    //response with the default ethernet connectino
    ctx.reply(`Ethernet Ip: ${os.networkInterfaces().eth0[0].address}`);
});

//reponse
bot.hears('hola', (ctx) => {
    ctx.reply('Hola ' + ctx.from.first_name + ' '+ ctx.from.last_name +  ' '+ messageToSend);
});


//Hears
bot.hears(['1','foto'], (ctx) => {
    if(serverisWorking) shutdownServer(ctx);
        ctx.reply('Enviando Foto...').then( () => {
        callOpenCv(1,ctx);
    });
});

bot.hears(['2','personas'], (ctx) => {
    if(serverisWorking) shutdownServer(ctx);

    fs.readdir('./Recognition/Data', (err, files) => {
        if(err){
            console.error(err);
            return;
        }
        if(files.length > 0){
            for(let i = 0; i < files.length; i++) personas += `- ${files[i]}`;
            ctx.reply(personas)
        }
    })
    personas = `Las personas que encontré en mi base de Datos fueron: `;

});
bot.hears(['3','audio'], (ctx) => {
    if(serverisWorking) shutdownServer(ctx);
    ctx.replyWithAudio({source: './assets/audioDePrueba.ogg'});
});

bot.hears(['4','video'], (ctx) => {
    if(serverisWorking) shutdownServer(ctx);

    ctx.reply('Espera un momento mientras grabamos el video :) ......').then(
    callOpenCv(4,ctx)).then(() => {
        setTimeout(() =>{
            led.writeSync(1);
        },1000)
    });
});

bot.hears(['5','reconocimiento'], (ctx) => {
    if(serverisWorking) shutdownServer(ctx);

    ctx.reply('Espera un momento mientras grabamos el video con reconocimiento facial :) ......')
    .then(callOpenCv(5,ctx));
});

bot.hears(['6','apagar'], (ctx) => {
    if(serverisWorking) shutdownServer(ctx);
    ctx.reply('¿Estás seguro que deseas apagar xD Ring?').then( () => confirm = true);
});


bot.hears(['7','server'],  (ctx) => {
    if(!serverisWorking){
        serverisWorking = true;
        createVideo().then(async () => {
            //if u r using raspbian therefore xdg-open utility should oupen; keep in mind to change if u r using another os
            const openClient = exec('xdg-open http://localhost:3000');

            //functions
            openClient.stdout.on('data', (data) => {
                console.log(data);
            });

            openClient.stdout.on('error', (err) => {
                console.error(err)
            });

            openClient.on('exit', (code) => {
                console.log(`exit with code : ${code}`);
            });

        });

        //send the default ethernet connection
        ctx.reply(`http://${os.networkInterfaces().eth0[0].address}:3000/visualizar.html`);
    }else {
        shutdownServer(ctx);
        ctx.reply('La transmisión en vivo se pausó con éxito :)');
    }
});

bot.hears('8', (ctx) => {
    ctx.reply('Estas a punto de agregar una persona a la lista de reconocimiento facial 😎, y hay unas consideraciones que debes tener antes de empezar 🤓');
    ctx.reply(`-Asegurate de que la persona a reguistrar no esté listada ya entre las personas con reconocimiento facial, puedes consultar las personas listadas ingresando 2
-Posicionate en el lugar donde está instalado el timbre, no lo cambie de su lugar usual, pues el mismo ambiente ayuda a tener un mejor reconocimiento.`);
    ctx.reply(`Recuerda que este es un proceso de 2 etapas:
- *Muestra: * Donde se graba un video de un minuto de la persona a reconocer, trata de hacer gestos y expresiones, siempre de frente a la cámara del timbre
- *Datos:* Donde se te pide el Nombre de la persona a reconocer.`);
    ctx.reply('Cuando estés listo para grabar la muestra de un minuto, envía un ok  😎');
    isOk = true;
});

bot.hears('9', (ctx)=> {
    setTimeout(() =>{
        door.writeSync(0);
    },1000);
    door.writeSync(1);
    ctx.reply('Puerta Abierta');
});

bot.hears('ok' , async (ctx) =>{
    if(isOk){
        ctx.reply('Empezamos a grabar la muestra en...');
        await ctx.reply('3');
        await ctx.reply('2');
        await ctx.reply('1');
        await ctx.reply('Estamos grabando...').then(callOpenCv(8,ctx));
    }
});

//Events

bot.on('voice', (ctx) => {

    console.log('There is a audio');
    bot.telegram.getFileLink(ctx.update.message.voice.file_id).then((link) => {
        console.log(link.href);
        open(link.href);        
    });   

});


bot.on('text', (ctx) => {
    console.log('Text');
    if(isOk && ctx.update.message.text.toLowerCase() != 'ok'){
        isOk = false;
        callOpenCv(9, ctx.update.message.text)
        console.log(ctx.update.message.text);
    }

    if(ctx.update.message.text.toLowerCase() == 'si' && confirm){
        ctx.reply('Apagando').then( () =>{
            console.log('apagando bot');
            confirm= false;
            callOpenCv(6);
        });
    }

    if(ctx.update.message.text.toLowerCase() == 'no' && confirm){
        ctx.reply('Ok, falsa alarma para mi 😮‍💨🤩').then( () =>{
        console.log('false alarma');
        confirm = false;
        });
    }

});



//deploy
bot.launch().then( () => {
    console.log('Bot inicado');
    checkButton();
});

let onceRing = false;
let onceNo = false;

const checkButton = () => {

    setInterval(() => {
        /*

        x = button.readSync();
        if(x == 0){
            if(!onceNo){
                mensaje = console.log('Botón no presionado');
                onceNo = true;}
                onceRing = false;
            } else if(onceRing == false){
                onceNo = false;
                console.log('Botón presionado');
                callOpenCv(7);
                onceRing = true;
            }
                */
    }, 300);
}

//methods

const callOpenCv = (action, parameter) => {
    confirm = false;
    obj = { action }
    const childPython = exec(` python3 ./computerVision/main.py ${action} ${parameter}`);

    childPython.stdout.on('data', (data) => {
        console.log(`stdout: ${data}`);
    });

    childPython.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
    });

    childPython.on('close', (data) => {
        console.log(`child process exited with code ${data}`);
        if(action == 1){
            parameter.replyWithPhoto({source: './assets/image.jpg'}).then(() => {
                console.log('Foto tomada con éxito');
            });
        }else if(action == 4 || action == 5){
            parameter.replyWithVideo({source: './assets/videoConReconocimiento.mp4'}).then(() => {
                console.log('Video Grabado con éxito');
                led.writeSync(0);
            });
        }else if(action == 6){
            console.log('apagando xD Ring');
        }else if (action == 7){
            if(peopleToSend.length==0){
                console.log('There is no users yet')
            }else{
            for(let i = 0; i < peopleToSend.length; i++){
                bot.telegram.sendPhoto(peopleToSend[i],{source: './assets/image.jpg'}).then(() => {
                    bot.telegram.sendMessage(peopleToSend[i],'Alguien ha tocado el timbre ');
                })
            }
        }
        }else if(action == 8){
            parameter.reply('El video de muestra se terminó de grabar con éxito').then(() =>{
                parameter.reply('Ingresa el nombre de la persona:');
            })
        }else if(action == 10){
            deleteFonderAudio();
            let checkFolder = setInterval(
                () => {
                    fs.readdir('./telegramBot/audio', (err, files) => {
                        if(files.length > 0){
                            callOpenCv(10, './telegramBot/audio/' + files[0]);
                            clearInterval(checkFolder)
                            console.log(files.length);
                        }
                    })
                }
            , 1000);
            
        }
    });

}

const createVideo = async () => { 
    http.listen(3000, () => {
        console.log('Servidor en el puerto 3000');
        serverisWorking = true;
    });
}


let checkFolder = setInterval(
    () => {
        fs.readdir('./telegramBot/audio', (err, files) => {
            if(files.length > 0){
                callOpenCv(10, './telegramBot/audio/' + files[0]);
                clearInterval(checkFolder)
                console.log(files.length);
            }
        })
    }
, 1000);
