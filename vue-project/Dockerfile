# This file is a template, and might need editing before it works on your project.
FROM node:8.11

WORKDIR vue-project/

ARG NODE_ENV
ENV NODE_ENV $NODE_ENV

COPY package.json vue-project/
RUN npm install

COPY . vue-project/

# replace this with your application's default port
EXPOSE 9999
CMD [ "npm", "start" ]
