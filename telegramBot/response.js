const startRecording = async (ctx, isOk)=> {
    if(isOk){
        ctx.reply('Empezamos a grabar la muestra en...');
        await ctx.reply('3');
        await ctx.reply('2');
        await ctx.reply('1');
        await ctx.reply('Estamos grabando...').then(callOpenCv(8,ctx));
    }

}

module.exports = {
    startRecording
}