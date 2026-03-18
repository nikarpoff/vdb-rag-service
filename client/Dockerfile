# build stage
FROM node:20-slim AS builder

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .
RUN npm run build


# runtime stage
FROM node:20-slim

WORKDIR /app

COPY --from=builder /app/dist ./dist
COPY package.json ./

RUN npm install --only=production

EXPOSE 3000

CMD ["npx", "serve", "dist"]