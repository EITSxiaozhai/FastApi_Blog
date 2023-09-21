# This file is a template, and might need editing before it works on your project.
FROM node:18.17.1

WORKDIR /usr/src/app

ARG NODE_ENV
ENV NODE_ENV $NODE_ENV

COPY package.json /usr/src/app/
RUN npm install -g npm
RUN npm install


COPY . /usr/src/app/
EXPOSE 5173
RUN npm run build
# replace this with your application's default port
CMD ["npm", "run" ,"serve-prod"]
