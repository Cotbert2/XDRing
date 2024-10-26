const fs = require('fs');

let checkFolder = setInterval(() => {
        fs.readdir('./telegramBot/audio', (err, files) => {
            if(files.length > 0){
                callOpenCv(10, './telegramBot/audio/' + files[0]);
                clearInterval(checkFolder)
                console.log(files.length);
            }
        })
    }
, 1000);

module.exports = {
    checkFolder
}