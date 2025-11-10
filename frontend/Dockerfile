# Etapa 1: Construcción
FROM node:18-alpine AS builder
WORKDIR /app
COPY . .
RUN npm install
RUN npm run build

# Etapa 2: Producción
FROM node:18-alpine AS runner
WORKDIR /app

# Copia la salida optimizada de 'standalone'
COPY --from=builder /app/.next/standalone ./

# Copia los archivos públicos y estáticos
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node", "server.js"]