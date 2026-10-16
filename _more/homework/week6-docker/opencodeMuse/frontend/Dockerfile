# ---- Node.js Frontend ----
FROM node:20-alpine

WORKDIR /app

COPY package.json ./
RUN npm install --omit=dev

COPY server.js ./
COPY public ./public

EXPOSE 3000
CMD ["npm", "start"]
