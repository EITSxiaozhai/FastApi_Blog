module.exports = {
  chainWebpack: (config) => {
    config.plugin('define').tap((args) => {
      const env = args[0];
      // 这里使用了 process.env.VUE_APP_API_URL，确保加载对应环境的 API 地址
      env['process.env']['VUE_APP_API_URL'] = JSON.stringify(process.env.VUE_APP_API_URL);
      return args;
    });
  },
};
