FROM node:20-alpine

WORKDIR /app

# Note: since the dev environment might not have node installed, 
# there might not be a package-lock.json. We use '*' to conditionally copy it.
COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 5173

# Start Vite dev server exposing to all local IP host interfaces
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
