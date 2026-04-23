from django.db.models.signals import post_delete
from django.dispatch import Signal
from django_tenants.utils import get_tenant_model, schema_exists


def _connect_tenant_post_delete():
    """Connect the post_delete signal scoped to the tenant model only.

    Using @receiver(post_delete) without a sender registers a catch-all
    listener that fires for every model delete.  Django's Collector checks
    has_listeners(model) and, when True, skips its "fast-delete" optimisation
    — forcing a SELECT + Python hydration + cascade walk even for models with
    no reverse FKs or signal handlers.

    By specifying sender=get_tenant_model() the listener only matches the
    tenant model, which is the only model this handler actually cares about.
    """
    post_delete.connect(
        tenant_delete_callback,
        sender=get_tenant_model(),
        dispatch_uid="django_tenants.signals.tenant_delete_callback",
    )

post_schema_sync = Signal()
post_schema_sync.__doc__ = """

Sent after a tenant has been saved, its schema created and synced

Argument Required = tenant

"""

schema_needs_to_be_sync = Signal()
schema_needs_to_be_sync.__doc__ = """
Schema needs to be synced

Argument Required = tenant

"""

schema_migrated = Signal()
schema_migrated.__doc__ = """
Sent after migration has finished on a schema

Argument Required = schema_name
"""


schema_pre_migration = Signal()
schema_pre_migration.__doc__ = """
Sent before migrations start on a schema

Argument Required = schema_name
"""


schema_migrate_message = Signal()
schema_migrate_message.__doc__ = """
Sent when a message is generated in run migration

Argument Required = message
"""


def tenant_delete_callback(sender, instance, **kwargs):
    if instance.auto_drop_schema and schema_exists(instance.schema_name):
        instance._drop_schema(True)
