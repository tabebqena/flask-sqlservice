from typing import Optional, TYPE_CHECKING
from flask import current_app, g

from sqlservice import Database, Session
if TYPE_CHECKING:
    from flask import Flask


class FlaskSQLService(object):

    """Flask extension for sqlservice.Database instance
    Main aim is to provide:
    - Flak extension style object for `sqlservice.Database`
    - Use `flask.configs` to provide parameters of `sqlservice.Database`.
    - Create database `Session` for each request & close it properly after the request finished.
    - The database session is available as `flask.g.dbsession`
    """

    def __init__(
        self,
        app: Optional["Flask"] = None,
        database_uri: Optional[str] = None,
        model_class=None,
        session_class=None,
        session_options=None,
        extension_key="database"
    ):
        """
        __init__ FlaskSQLService initiator

        :param app: The flask app instance, defaults to None
        :type app: Flask, optional
        :param database_uri: The database uri, defaults to None
        :type database_uri: str, optional
        :param model_class: The declarative class that all models inherit from if, 
        specifiying this parameter here or from `app.config` is very important. If
        you passed `None` This means that all your models are inheriting from 
        `sqlservice.ModelBase`
        defaults to None
        :type model_class: _type_, optional
        :param session_class: The session class used by database, defaults to None
        which means that `sqlservice.Session` will be used
        :type session_class: _type_, optional
        :param session_options: options that will be passed to `Session` class when initialized, defaults to None
        :type session_options: _type_, optional
        :param extension_key: the key that will be used to store this instance in `flask.extensions` dictionary,
        You can pass any value & support multiple database instances.
         defaults to "database"
        :type extension_key: str, optional
        """
        self.model_class = model_class
        self.session_class = session_class
        self.session_options = session_options or {}
        self.key = extension_key

        if app:
            self.init_app(app, database_uri)

    def init_app(self, app: "Flask", uri=None):
        """
        init_app init sqlservice database by the configs specified in the app

        If you pass `app` to the `FlaskSQLService` constructor, This method will be called
        from the constructor.
        If you pass `None` to the constructor, You should call this method in somewhere.

        :param app: The flask app instance
        :type app: Flask
        :param database_uri: The database uri, defaults to None
        which means that `app.config[`SQL_DATABASE_URI`]` will be used.
        if this value is also `None`, ValueError will be raised.
        :type database_uri: str, optional
        :raises ValueError: raised if `uri` parameter & `app.config[`SQL_DATABASE_URI`]` are None
        :return: None
        :rtype: None
        """

        options = {}
        uri = uri or app.config.get("SQL_DATABASE_URI")
        if not uri:
            raise ValueError("Database uri can't be `None`")
        options["model_class"] = self.model_class or app.config.get(
            "SQL_MODEL_CLASS"
        )
        session_class = self.session_class or app.config.get(
            "SQL_SESSION_CLASS"
        )
        if session_class:
            options["session_class"] = session_class

        options["autoflush"] = app.config.get("SQL_AUTOFLUSH")
        options["expire_on_commit"] = app.config.get("SQL_EXPIRE_ON_COMMIT")

        options["isolation_level"] = app.config.get("SQL_ISOLATION_LEVEL")
        options["pool_size"] = app.config.get("SQL_POOL_SIZE")
        options["pool_timeout"] = app.config.get("SQL_POOL_TIMEOUT")
        options["pool_recycle"] = app.config.get("SQL_POOL_RECYCLE")
        options["pool_pre_ping"] = app.config.get("SQL_POOL_PRE_PING")
        options["poolclass"] = app.config.get("SQL_POOL_CLASS")
        options["max_overflow"] = app.config.get("SQL_MAX_OVERFLOW")
        options["paramstyle"] = app.config.get("SQL_PARAM_STYLE")

        options["encoding"] = app.config.get("SQL_ENCODING")
        options["execution_options"] = app.config.get("SQL_EXECUTION_OPTIONS")

        options["echo"] = app.config.get("SQL_ECHO")
        options["echo_pool"] = app.config.get("SQL_ECHO_POOL")
        options["engine_options"] = app.config.get("SQL_ENGINE_OPTIONS")
        options["session_options"] = self.session_options

        # Store Database instances on app.extensions so it can be accessed
        # through flask.current_app proxy.
        app.extensions[self.key] = Database(uri=uri, **options)

        # Ensure that the session is closed on app context teardown so we
        # don't leave any sessions open after the request ends.
        @app.after_request
        def shutdown_session(response_or_exc):
            g.dbsession.close()
            return response_or_exc

        @app.before_request
        def create_dbsession():
            autoflush = current_app.config.get("SQL_AUTOFLUSH")
            expire_on_commit = current_app.config.get("SQL_EXPIRE_ON_COMMIT")
            # Create session
            g.dbsession = self.db().session(
                autoflush=autoflush, expire_on_commit=expire_on_commit
            )

    def db(self) -> Database:
        return current_app.extensions[self.key]

    @staticmethod
    def session() -> Session:
        return g.dbsession
