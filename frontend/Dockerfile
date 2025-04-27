FROM node:18-alpine

RUN apk add g++ make py3-pip
RUN apk add --no-cache libc6-compat git

WORKDIR /app

# only copy package.json
COPY package*.json ./

RUN npm install

# copy source code
COPY . .

# test environment build
ARG NODE_ENV=development
ENV NODE_ENV=${NODE_ENV}

# if test environment, choose not to build
RUN if [ "$NODE_ENV" = "production" ]; then npm run build; fi

EXPOSE 3000

# default startup command depends on environment variable
CMD ["sh", "-c", "if [ \"$NODE_ENV\" = \"production\" ]; then npm start; else npm run dev; fi"]