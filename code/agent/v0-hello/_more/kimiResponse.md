(.venv) cccuser@cccimacdeiMac 01-hello % python kimi1.py
Traceback (most recent call last):
  File "/Users/Shared/ccc/115a/se/_code/01/01-hello/kimi1.py", line 9, in <module>
    completion = client.chat.completions.create(
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/cccuser/.venv/lib/python3.11/site-packages/openai/_utils/_utils.py", line 298, in wrapper
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/Users/cccuser/.venv/lib/python3.11/site-packages/openai/resources/chat/completions/completions.py", line 1215, in create
    return self._post(
           ^^^^^^^^^^^
  File "/Users/cccuser/.venv/lib/python3.11/site-packages/openai/_base_client.py", line 1332, in post
    return cast(ResponseT, self.request(cast_to, opts, stream=stream, stream_cls=stream_cls))
                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/cccuser/.venv/lib/python3.11/site-packages/openai/_base_client.py", line 1105, in request
    raise self._make_status_error_from_response(err.response) from None
openai.RateLimitError: Error code: 429 - {'error': {'message': 'Your account org-93604ae3bd384bec999743d1f403c9f6 <ak-fcd87t5s13t111eudhpi> is suspended due to insufficient balance, please recharge your account or check your plan and billing details', 'type': 'exceeded_current_quota_error'}}