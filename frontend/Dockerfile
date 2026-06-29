# --- Tadna Insta frontend (Next.js 14) ---
FROM node:20-slim

WORKDIR /app

# .npmrc already points npm at the Liara mirror with generous retry settings.
COPY package.json package-lock.json .npmrc ./
RUN npm ci

# App source + production build.
COPY . .
RUN npm run build

EXPOSE 3000

# Production command. The dev override swaps this for `npm run dev`.
CMD ["npm", "start"]
