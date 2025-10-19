class BaseRouter:
    """
    A router to control all database operations on models in the
    auth and contenttypes applications.
    """
    db_name = 'base'
    route_app_labels = {db_name,}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return self.db_name
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return self.db_name
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == self.db_name
        return None

class LogRouter(BaseRouter):
    db_name = 'log'
    route_app_labels = {db_name,}

class RoemailRouter(BaseRouter):
    db_name = 'roemail'
    route_app_labels = {db_name,}