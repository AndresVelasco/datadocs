class DatadocsError(Exception):
    """Base exception for datadocs."""


class TemplateError(DatadocsError):
    """Raised when a template cannot be loaded or rendered."""


class DataLoadError(DatadocsError):
    """Raised when structured data cannot be loaded."""


class SourceError(DatadocsError):
    """Raised when a source cannot load data."""


class ConfigurationError(DatadocsError):
    """Raised when datadocs is configured incorrectly."""

