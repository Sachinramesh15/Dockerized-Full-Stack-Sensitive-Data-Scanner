# Use the official Nginx image as the base image
FROM nginx:alpine

# Set the working directory inside the container
WORKDIR /usr/share/nginx/html

# Copy the static frontend files (HTML, CSS, JS) into the Nginx directory
COPY frontend /usr/share/nginx/html

# Expose the port 5500 for the frontend
EXPOSE 5500

# No need to run any additional command; Nginx will automatically serve the files
