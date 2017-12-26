module.exports = {
  /**
   * Application configuration section
   * http://pm2.keymetrics.io/docs/usage/application-declaration/
   */
  apps : [

    // First application
    {
      name      : 'API',
      script    : 'app.js',
      env: {
        COMMON_VARIABLE: 'true'
      },
      env_production : {
        NODE_ENV: 'production'
      }
    }
  ],

  /**
   * Deployment section
   * http://pm2.keymetrics.io/docs/usage/deployment/
   */
  deploy : {
    production : {
      user : 'scan',
      host : 'docker.scherer.me',
      ref  : 'origin/master',
      repo : 'git@bitbucket.org:scansoft/fw-tool.git',
      path : '/opt/fw-tool',
      'post-deploy' : 'docker exec FW-Tool "pm2 reload ecosystem.config.js --env production"'
    }
  }
};
