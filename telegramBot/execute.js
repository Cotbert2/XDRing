const { exec } = require('child_process');
const fs = require('fs');


const deleteFolderAudio = (http) => {
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

const shutdownServer = (contextXd, http) => {
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
        });
        tasks.on('exit', (code) => {
            console.log(`exit with code : ${code}`);

        });
        http.close();
        contextXd.reply('La transmisión en vivo se apagó correctamente');
}

module.exports = {
    deleteFolderAudio, shutdownServer
}