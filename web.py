#!/usr/bin/env python

from flask import Flask, request, render_template_string
import crawl

app = Flask(__name__)

@app.route('/search', methods=['GET'])
def search_page():
    query = request.args.get('query', '')
    results = app.server.search(query) if query else []
    return render_template_string(HTML_TEMPLATE, query=query, results=results)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Скопинский уезд</title>
</head>
<body>
    <form action="/search" method="get">
        <input type="text" name="query" value="{{ query }}" placeholder="Enter search term">
        <button type="submit">Search</button>
    </form>
    {% if results %}
        <ol>
        {% for result in results %}
            <li>{{ result }}</li>
        {% endfor %}
        </ol>
    {% endif %}
</body>
</html>
'''

if __name__ == '__main__':
    app.server = crawl.Server(crawl.SERVICE_ACCOUNT_FILE)
    app.run(debug=True)
