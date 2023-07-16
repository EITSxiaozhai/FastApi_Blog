# This file is a template, and might need editing before it works on your project.
FROM node:16.18.1


ARG NODE_ENV
ENV NODE_ENV $NODE_ENV

COPY package.json /usr/src/app/
RUN npm install -g npm
RUN npm install


# replace this with your application's default port
CMD [ "npm", "run" , "build"]
CMD [ "npm", "run" , "serve","-s","dist","--","--host","0.0.0.0"]
