import logging
import uvicorn
from fastapi import FastAPI
from app.core.otlp.utils import PrometheusMiddleware, metrics, setting_otlp, EndpointFilter
from app.config import app_config
from app.core.fastapi.routers import health, test
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title=app_config.app_name, description=app_config.app_name+" API", version="0.1.0")

# Setting metrics middleware
app.add_middleware(PrometheusMiddleware, app_name=app_config.app_name)
app.add_route("/metrics", metrics)
# include routers
app.include_router(health.router)
app.include_router(test.router, prefix="/test", tags=["test"])

# Set all CORS enabled origins
origins = [
    "*"
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["DELETE", "GET", "POST", "PUT","OPTIONS"],
    allow_headers=["*"],
)

# Setting OpenTelemetry exporter
setting_otlp(app, app_config.app_name, app_config.otlp_grpc_endpoint)

# Filter out /endpoint
logging.getLogger("uvicorn.access").addFilter(EndpointFilter())
logging.basicConfig(level=logging.INFO)


def start():
    
    # update uvicorn access logger format
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = "%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] [trace_id=%(otelTraceID)s span_id=%(otelSpanID)s resource.service.name=%(otelServiceName)s] - %(message)s"
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(app_config.port),
        log_config=log_config,
        workers=4,  # Adjust the number of workers based on your server's capabilities
        reload=False  # Enable auto-reload during development
    )