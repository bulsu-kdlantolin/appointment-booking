from django.shortcuts import render


class Custom404Middleware:
    """
    Ensures that any 404 response (including in DEBUG=True development)
    renders the project's styled 404.html template rather than Django's
    technical debug page. Also disables caching during development so
    browsers always receive up-to-date templates and static assets.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 404:
            # Don't intercept static file 404s
            if not request.path.startswith("/static/"):
                response = render(request, "404.html", status=404)
        response["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"
        return response

