# This file is a template, and might need editing before it works on your project.
FROM node:16.18.1

WORKDIR /usr/src/app

ARG NODE_ENV
ENV NODE_ENV $NODE_ENV

COPY package.json /usr/src/app/
RUN npm install -g npm
RUN npm install

COPY . /usr/src/app/
# replace this with your application's default port
CMD ["npm", "run", "build"]
CMD ["npm", "run" ,"serve","-s","dist","--","--host"]
