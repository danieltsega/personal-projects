# app.py

import http.server
import socketserver
import os
import cgi

class TinyWebFrameworkHandler(http.server.SimpleHTTPRequestHandler):
    # Define a dictionary to store URL mappings
    routes = {}

    # Add a method to register URL handlers
    @classmethod
    def add_route(cls, path, handler):
        cls.routes[path] = handler

    def do_GET(self):
        # Check if the requested URL starts with "/static/"
        if self.path.startswith("/static/"):
            self.serve_static_file()
        else:
            # Check if the requested URL is in the routes dictionary
            handler = self.routes.get(self.path)
            if handler:
                # Call the handler function if found
                handler(self)
            else:
                # If not found, return a 404 Not Found response
                self.send_error(404, "Not Found")

    def do_POST(self):
        # Parse the form data
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST'}
        )

        # Process the form data
        # For demonstration purposes, we'll just print the form values
        for field in form.keys():
            self.log_message("%s: %s" % (field, form[field].value))

        # Send a simple response
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Form submission received!")

    def serve_static_file(self):
        # Remove "/static/" prefix from the requested URL
        file_path = self.path[8:]
        # Construct the full file path
        file_path = os.path.join("static", file_path)

        # Check if the file exists
        if os.path.exists(file_path) and os.path.isfile(file_path):
            # Send the file contents as the response
            with open(file_path, "rb") as file:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(file.read())
        else:
            # If the file doesn't exist, return a 404 Not Found response
            self.send_error(404, "Not Found")

# Define a simple handler function for the home page
# app.py

# Import the os module
import os

# Import the template engine
from string import Template

# Routing mapping of URLs to component names
# For example: "/" maps to "home", "/about" maps to "about", etc.
ROUTES = {
    "/": "home",
    "/about": "about",
    "/contact": "contact"
}

def load_components():
    components = {}
    components_dir = "components"
    for filename in os.listdir(components_dir):
        if filename.endswith(".html"):
            component_name = os.path.splitext(filename)[0]
            with open(os.path.join(components_dir, filename), "r") as file:
                components[component_name] = file.read()
    return components

def home_page_handler(request_handler):
    with open(os.path.join("templates", "index.html"), "r") as file:
        template = Template(file.read())


    static_components = load_components()

    navbar_content = static_components.get("navbar", "")
    footer_content = static_components.get("footer", "")

    # Get the requested URL
    requested_url = request_handler.path
    print("Requested URL:", requested_url)

    # Get the corresponding component name from the ROUTES mapping
    component_name = ROUTES.get(requested_url)
    print("Corresponding Component:", component_name)

    if component_name:
        components = load_components()
        component_content = components.get(component_name, "")
    else:
        component_content = "<h1>404 Not Found</h1>"

    # Inject the component content into the main content div of the template
    rendered_html = template.safe_substitute(main_content=component_content, navbar=navbar_content, footer=footer_content)

    request_handler.send_response(200)
    request_handler.send_header("Content-type", "text/html")
    request_handler.end_headers()
    request_handler.wfile.write(rendered_html.encode("utf-8"))


TinyWebFrameworkHandler.add_route("/", home_page_handler)
TinyWebFrameworkHandler.add_route("/about", home_page_handler)
TinyWebFrameworkHandler.add_route("/contact", home_page_handler)

def run_server():
    PORT = 8000
    with socketserver.TCPServer(("", PORT), TinyWebFrameworkHandler) as httpd:
        print("Server started on port", PORT)
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()

