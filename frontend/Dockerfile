FROM docker.m.daocloud.io/library/node:18-slim

# Set work directory
WORKDIR /app

# Use Chinese npm registry
RUN npm config set registry https://registry.npmmirror.com

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy project files
COPY . .

# Build the application
RUN npm run build

# Expose port 4000
EXPOSE 4000

# Set environment variable for port
ENV PORT=4000

# Start the application
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "4000"]