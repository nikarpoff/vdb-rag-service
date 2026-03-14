FROM node:20-alpine

WORKDIR /app

COPY client/package.json client/package-lock.json* ./

RUN npm ci --only=production

COPY client/ .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
