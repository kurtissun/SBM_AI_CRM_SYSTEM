FROM docker.m.daocloud.io/library/node:24-alpine3.21

WORKDIR /app

ENV npm_config_loglevel=warn \
    npm_config_audit=false \
    npm_config_fund=false

# If you really need a mirror, uncomment:
# RUN npm config set registry https://registry.npmmirror.com
RUN npm config set registry https://registry.npmjs.org

COPY package.json ./

# Install deps
RUN npm install

# Copy source
COPY . .

# Vite dev server
EXPOSE 4000
ENV HOST=0.0.0.0
ENV PORT=4000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "4000"]