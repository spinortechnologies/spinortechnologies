# Stage 1: Build
FROM node:18-alpine AS builder
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source and build
COPY . .
RUN npm run build

# Stage 2: Production Runtime
FROM node:18-alpine
WORKDIR /app

# Copy runtime dependencies
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules

# Security hardening
RUN chown -R node:node /app
USER node

EXPOSE 3000
ENV NODE_ENV production
CMD ["npm", "start"]