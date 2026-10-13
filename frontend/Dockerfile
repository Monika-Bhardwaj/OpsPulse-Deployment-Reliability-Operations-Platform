FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci --prefer-offline
COPY . .
RUN npm run build

FROM nginx:stable-alpine
# Create non-root user and configure nginx for unprivileged execution
RUN apk upgrade --no-cache

RUN addgroup -g 10001 -S appgroup && adduser -u 10001 -S appuser -G appgroup \
    && sed -i 's,/run/nginx.pid,/tmp/nginx.pid,g' /etc/nginx/nginx.conf \
    && sed -i '/^user /d' /etc/nginx/nginx.conf \
    && chown -R appuser:appgroup /var/cache/nginx /var/log/nginx /etc/nginx /tmp /usr/share/nginx/html

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Switch to non-root user
USER 10001

EXPOSE 8080

# Default backend hostname for docker compose networking.
# The Helm chart overrides this with the backend Service name.
ENV BACKEND_HOST=backend

# Render the backend hostname into the nginx config at container start.
# Only $BACKEND_HOST is substituted so nginx variables ($host, $uri, …)
# are left untouched.
CMD ["sh", "-c", "envsubst '${BACKEND_HOST}' < /etc/nginx/conf.d/default.conf > /tmp/default.conf && cp /tmp/default.conf /etc/nginx/conf.d/default.conf && exec nginx -g 'daemon off;'"]
