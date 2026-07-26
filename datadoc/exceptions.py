class DatadocError(Exception):
    """Base exception for datadoc."""


class TemplateError(DatadocError):
    """Raised when a template cannot be loaded or rendered."""


class DataLoadError(DatadocError):
    """Raised when structured data cannot be loaded."""


class SourceError(DatadocError):
    """Raised when a source cannot load data."""


class ConfigurationError(DatadocError):
    """Raised when datadoc is configured incorrectly."""

