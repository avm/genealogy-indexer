#!/usr/bin/env python

from flask import Flask, request, render_template_string
import argparse
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
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta charset="utf-8" />
    <title>Скопинский уезд</title>
</head>
<body>
    <form action="/search" method="get">
        <input type="text" name="query" style="width: 500px;"
          value="{{ query }}" placeholder="Enter search term">
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
    parser = argparse.ArgumentParser()
    parser.add_argument('--endpoint', default='127.0.0.1:5000')
    parser.add_argument('--account-file', default=crawl.SERVICE_ACCOUNT_FILE)
    args = parser.parse_args()

    app.server = crawl.Server(args.account_file)
    host, _, port = args.endpoint.rpartition(':')
    app.run()
