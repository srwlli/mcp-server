"""Minimal test to see if Railway can import anything at all."""

print("=" * 80)
print("TEST_APP.PY IS LOADING")
print("=" * 80)

from flask import Flask

print("Flask imported successfully")

app = Flask(__name__)

print(f"App created: {app}")
print(f"App type: {type(app)}")

@app.route('/test')
def test():
    return {'status': 'test app works'}

print("Routes registered")
print("=" * 80)
print("TEST_APP.PY LOADED SUCCESSFULLY")
print("=" * 80)
