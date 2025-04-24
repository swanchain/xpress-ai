FROM node:18-alpine

RUN apk add g++ make py3-pip
RUN apk add --no-cache libc6-compat git

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .
COPY .env.production .env.local

RUN npm run build

EXPOSE 3000

ENV NODE_ENV=production

CMD ["npm", "start"]