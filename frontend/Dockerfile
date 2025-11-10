# Etapa 1: Construcción
FROM node:20-alpine AS builder
WORKDIR /app
COPY . .
RUN npm install
RUN npm run build

# Etapa 2: Producción
FROM node:20-alpine AS runner
WORKDIR /app

# Copia la salida optimizada de 'standalone'
COPY --from=builder /app/.next/standalone ./

# Copia los archivos públicos y estáticos
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/static ./.next/static

# Cloud Run sets PORT env variable, default to 3000 for local dev
ENV PORT=3000
EXPOSE $PORT

CMD ["sh", "-c", "PORT=${PORT} node server.js"]