"""W2-B2 provider boundary. Live protocol is unverified and disabled."""
from dataclasses import dataclass
import math
from . import feasibility as f

TOTAL_TIMEOUT_SECONDS = 60
RESPONSE_LIMIT = 64 * 1024


@dataclass(frozen=True)
class ProviderResult:
    request_id: str
    model: str | None
    finish_state: str | None
    content: bytes | None
    usage: dict | None
    failure_code: str | None
    synthetic: bool


def request_explanation(approved_payload, call_policy):
    # No credentials are read, no HTTP client is constructed, no fallback route.
    if call_policy is None:
        f.fail('call_policy_not_configured')
    f.fail('live_provider_protocol_not_verified')


def read_mock_response(started_at, clock, connection, response):
    """Controlled fake I/O only. Caller starts the deadline before fake send.

    Connection.settimeout receives remaining *overall* time before each read.
    This helper does not construct HTTP, read credentials or follow any URL.
    """
    if type(started_at) not in (int, float) or not math.isfinite(started_at):
        f.fail('mock_deadline_invalid')
    if type(response.status) is not int:
        f.fail('mock_http_status_invalid')
    if 300 <= response.status < 400:
        f.fail('mock_redirect_rejected')
    if response.status != 200:
        f.fail('mock_http_error')
    chunks, length = [], 0
    while True:
        current = clock()
        if type(current) not in (int, float) or not math.isfinite(current) or current < started_at:
            f.fail('mock_deadline_invalid')
        remaining = TOTAL_TIMEOUT_SECONDS - (current - started_at)
        if remaining <= 0:
            f.fail('mock_total_timeout')
        connection.settimeout(remaining)
        # Read one beyond the remaining limit to reject, never silently truncate.
        chunk = response.read(min(4096, RESPONSE_LIMIT + 1 - length))
        after = clock()
        if type(after) not in (int, float) or not math.isfinite(after) or after < current:
            f.fail('mock_deadline_invalid')
        if after - started_at >= TOTAL_TIMEOUT_SECONDS:
            f.fail('mock_total_timeout')
        if type(chunk) is not bytes:
            f.fail('mock_response_chunk_type')
        length += len(chunk)
        if length > RESPONSE_LIMIT:
            f.fail('response_size_boundary')
        if not chunk:
            return b''.join(chunks)
        chunks.append(chunk)


def mock_result(request_id, model, content, usage=None, finish_state='stop'):
    """Test data only; cannot be converted into a live calling authorization."""
    f.identifier(request_id)
    f.identifier(model)
    if type(content) is not bytes:
        f.fail('mock_content_type')
    if len(content) > RESPONSE_LIMIT:
        return ProviderResult(request_id, model, finish_state, None, usage,
                              'response_size_boundary', True)
    return ProviderResult(request_id, model, finish_state, content, usage, None, True)
