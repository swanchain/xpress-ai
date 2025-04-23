FROM node:18-alpine

RUN apk add g++ make py3-pip
RUN apk add --no-cache libc6-compat git

WORKDIR /app

COPY package*.json ./
COPY jsconfig.json ./

RUN npm install
RUN npm install axios
RUN npm install --save-dev @types/react @types/node @types/js-cookie @types/react-toastify @types/react-redux @types/next
RUN npm install react-datepicker @types/react-datepicker

COPY . .
COPY .env.production .env.local

# # Set build-time variables (arguments)
# ARG NEXT_PUBLIC_BASE_URL

# # Set environment variables for the container
# ENV NEXT_PUBLIC_BASE_URL=$NEXT_PUBLIC_BASE_URL

RUN npm run build

EXPOSE 3000

ENV NODE_ENV=production

CMD ["npm", "start"]