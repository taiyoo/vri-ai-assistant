FROM public.ecr.aws/docker/library/node:22-bullseye-slim

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci


COPY . .
RUN npm run build

EXPOSE 5173

CMD ["npm", "run", "dev"]
