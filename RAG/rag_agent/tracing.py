import warnings
from typing import Optional

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

from phoenix.otel import register
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from openinference.instrumentation.google_adk import GoogleADKInstrumentor


def instrument_adk_with_phoenix() -> Optional[trace.Tracer]:
    """
    Instrument the Google ADK with Phoenix (local OpenInference tracing).

    This sets up:
    - An OpenTelemetry TracerProvider
    - A Phoenix exporter (local UI)
    - Google ADK auto-instrumentation
    """

    try:
        # Register with Phoenix / OpenInference
        tracer_provider = register(project_name="adk-rag-agent", batch=True)
    except Exception as e:
        warnings.warn(f"Failed to initialize Phoenix tracing: {e}")
        return None

    # Instrument Google ADK so agent + tool calls emit OpenInference spans
    GoogleADKInstrumentor().instrument(
        tracer_provider=tracer_provider
    )

    return tracer_provider.get_tracer(__name__)
