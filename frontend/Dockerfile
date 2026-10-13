FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci --prefer-offline
COPY . .
RUN npm run build

FROM nginx:1.27-alpine
# Create non-root user for nginx
RUN addgroup -g 10001 -S appgroup && adduser -u 10001 -S appuser -G appgroup \
    && touch /tmp/nginx.pid \
    && chown -R appuser:appgroup /tmp/nginx.pid /var/cache/nginx /var/log/nginx /etc/nginx/conf.d

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Switch to non-root user
USER 10001

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
