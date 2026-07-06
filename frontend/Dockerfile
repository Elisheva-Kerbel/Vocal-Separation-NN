# StemSpace frontend — Phase 0 Vite + React empty-shell image (P0-005).
#
# Minimal Node base that installs only the frontend dependencies and runs the
# Vite dev server for the Phase 0 empty shell. No product UI, no backend API
# calls, no secrets baked in. docker-compose maps the host FRONTEND_PORT to the
# container's Vite port (5173).
FROM node:20-alpine

WORKDIR /app

# Install dependencies first for better layer caching. package*.json matches
# package.json (and package-lock.json when present) so installs are reproducible.
COPY package*.json ./
RUN npm install

# Application code (see .dockerignore for what is excluded, e.g. node_modules).
COPY . .

# Vite dev server listens on 5173; docker-compose maps the host FRONTEND_PORT.
EXPOSE 5173

# --host 0.0.0.0 makes the dev server reachable from the host (also set in
# vite.config.js). docker-compose does not override this command.
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
