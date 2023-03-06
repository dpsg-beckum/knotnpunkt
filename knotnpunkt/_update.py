from alembic import config, script
from alembic.runtime import migration
from alembic.command import upgrade
from sqlalchemy import engine
import logging

logger = logging.getLogger(__name__)


class DatabaseMigrationError(Exception):
    pass


def check_current_head(
        alembic_cfg: config.Config,
        connectable: engine.Engine) -> bool:
    """Checks if existing database matches given revision scripts.

    Args:
        `alembic_cfg` (config.Config): Alembic configuration
        `connectable` (engine.Engine): SQLAlchemy engine

    Returns:
        bool: True if database is up to date, False if heads do not match.
    """
    # Load alembic config
    directory = script.ScriptDirectory.from_config(alembic_cfg)
    # Beginn database connection
    with connectable.begin() as connection:
        context = migration.MigrationContext.configure(connection)
        logger.info(f"Your database is at {context.get_current_heads()}, the latest available version is {directory.get_heads()}, ")
        return set(context.get_current_heads()) == set(directory.get_heads())


def apply_upgrade(alembic_cfg: config.Config):
    """Update database schema on software update. In the future we could test 
    for multiple heads in unittests.

    Args:
        alembic_cfg (config.Config): Alembic configuration

    Raises:
        DatabaseMigrationError: Prevents automatic updates when multiple heads exist.
    """
    # Load alembic config
    directory = script.ScriptDirectory.from_config(alembic_cfg)
    if len(directory.get_heads()) > 1:
        # Auto-update needs one single head revision to work
        msg = f"Existing heads: {directory.get_heads()}. Merge alembic branches and retry automatic update."
        raise DatabaseMigrationError(msg)
    upgrade(alembic_cfg, "head")
